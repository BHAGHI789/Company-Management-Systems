import json
import hashlib
import logging
import secrets
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.offline as opy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import View
import plotly.graph_objects as go
from plotly.offline import plot
from .models import Analysis
from .models import *
from django.conf import settings as django_settings
import pandas as pd
import random
import base64
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization


KEYS_DIR = Path(__file__).resolve().parent.parent / "keys"   # adjust path if needed
print("KEYS_DIR", KEYS_DIR)
with open(KEYS_DIR / "private_key.pem", "rb") as f:
    PRIVATE_KEY = serialization.load_pem_private_key(f.read(), password=None)

with open(KEYS_DIR / "public_key.pem", "rb") as f:
    PUBLIC_KEY_PEM = f.read()          # we will send the DER form to frontend


def get_public_key_der_b64():
    """Return pure Base64 DER of the public key (what Web Crypto wants)."""
    public_key = PRIVATE_KEY.public_key()
    der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return base64.b64encode(der).decode("ascii")


def decrypt_value(encrypted_b64: str) -> str:
    """Decrypt a value that was encrypted with the public key on the frontend."""
    if not encrypted_b64:
        raise ValueError("Empty encrypted value")

    # Frontend sometimes replaces + with space in transit
    encrypted_b64 = encrypted_b64.replace(" ", "+")
    encrypted_bytes = base64.b64decode(encrypted_b64)

    # Web Crypto uses RSA-OAEP with SHA-256
    decrypted = PRIVATE_KEY.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted.decode("utf-8")


# -------------------------------------------------
# Views
# -------------------------------------------------
def get_public_key(request):
    return JsonResponse({
        "public_key": get_public_key_der_b64()
    })




class Login(View):
    @method_decorator(ensure_csrf_cookie)
    def get(self,request, *args, **kwargs):
        logout(request)
        return render(request, 'login.html')

    def post(self, request, *args, **kwargs):
        contenttype = request.META.get('CONTENT_TYPE', None)
        data_dict = None
        if 'json' in contenttype:
            #log.debug("json request body is %s", request.body)
            try:
                data_dict = json.loads(request.body.decode('utf-8'))
            except Exception as e:
                log.exception(e)
        elif contenttype == 'application/x-www-form-urlencoded':
            log.debug("content type is application/x-www-form-urlencoded ")
            data_dict = request.POST
        else:
            log.debug('Unknown ContentType: %s', contenttype)
            pdr = HttpResponse(status=400)
            pdr.write('Unknown HTTP ContentTye')
            return pdr
        try:

            import pdb; pdb.set_trace()
            if data_dict.get("status") == "credentials_verified":
                print("credentials")
                email = decrypt_value(data_dict.get("email"))
                password = decrypt_value(data_dict.get("password"))
                

                user = get_user_model().objects.filter(email__iexact=email).first()
                authenticated_user = (
                    authenticate(request, username=user.username, password=password)
                    if user is not None else None
                )

                if authenticated_user:


                    otp = secrets.randbelow(900000) + 100000
                    print("Generated OTP:", otp)
                    OTPValues.objects.update_or_create(
                        email=authenticated_user.email,
                        defaults={
                            "otp": str(otp),
                            "createdBy": authenticated_user,
                            "updatedBy": authenticated_user,
                        }
                    )
                    request.session['login_otp'] = {
                        "user_id": str(authenticated_user.pk),
                        "otp_hash": hashlib.sha256(str(otp).encode()).hexdigest(),
                        "expires_at": (timezone.now() + timedelta(minutes=10)).isoformat(),
                    }
                    resp = HttpResponse(content_type="application/json", status=200)
                    resp.write(json.dumps({"success": True, "status": "otp_sent"}))
                    return resp


                resp = HttpResponse(content_type="application/json", status=401)
                resp.write(json.dumps({"success": False, "message": "Invalid email or password."}))
                return resp
            if data_dict.get("status") == "otp_verify_testing":

                login_otp = request.session.get('login_otp')
                otp = str(data_dict.get("otp", "")).strip()
                import pdb; pdb.set_trace()
                if not login_otp:
                    resp = HttpResponse(content_type="application/json", status=400)
                    resp.write(json.dumps({"success": False, "message": "Request a new OTP first."}))
                    return resp



                
            if data_dict.get("status") == "otp_verify":
                login_otp = request.session.get('login_otp')
                otp = str(data_dict.get("otp", "")).strip()

                if not login_otp:
                    resp = HttpResponse(content_type="application/json", status=400)
                    resp.write(json.dumps({"success": False, "message": "Request a new OTP first."}))
                    return resp

                if timezone.now() > timezone.datetime.fromisoformat(login_otp["expires_at"]):
                    request.session.pop('login_otp', None)
                    resp = HttpResponse(content_type="application/json", status=400)
                    resp.write(json.dumps({"success": False, "message": "This OTP has expired."}))
                    return resp

                if not secrets.compare_digest(hashlib.sha256(otp.encode()).hexdigest(), login_otp["otp_hash"]):
                    resp = HttpResponse(content_type="application/json", status=400)
                    resp.write(json.dumps({"success": False, "message": "Invalid OTP."}))
                    return resp

                otp_user = get_user_model().objects.filter(pk=login_otp["user_id"]).first()
                request.session.pop('login_otp', None)
                if otp_user is None:
                    resp = HttpResponse(content_type="application/json", status=400)
                    resp.write(json.dumps({"success": False, "message": "Account was not found."}))
                    return resp

                # login() creates the session; Django sends the sessionid cookie with this response
                login(request, otp_user)
                resp = HttpResponse(content_type="application/json", status=200)
                resp.write(json.dumps({"success": True, "status": "signed_in"}))
                return resp

            resp = HttpResponse(content_type="application/json", status=200)
            resp.write(json.dumps({"znid": "znobj.id", "details": data_dict}))
            return resp
        except Exception as e:
            resp = HttpResponse(json.dumps(data_dict), content_type='application/json', status=400)
            return resp


class EmployeeList(View):
    def get(self, request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        # employeesDf = pd.DataFrame(Employees.objects.all().values("employeeName", "employeeId", "employeeEmail", "employeePhone", "employeeAddress", "employeeDepartment", "employeeDesignation", "employeeSalary", "employeeJoiningDate", "employeeStatus", "employeeCreatedAt", "employeeUpdatedAt"))
        
        return render(request, 'employeeList.html', locals())





def serialize_report(report):
    return {
        'name': report.report_name,
        'frequency': float(report.frequency),
        'frequencyMin': float(report.frequencyMin),
        'frequencyMax': float(report.frequencyMax),
        'frequencyAvg': float(report.frequencyAvg),
        'pri': float(report.pri),
        'priMin': float(report.priMin),
        'priMax': float(report.priMax),
        'priAvg': float(report.priAvg),
        'pw': float(report.pw),
        'pwMin': float(report.pwMin),
        'pwMax': float(report.pwMax),
        'pwAvg': float(report.pwAvg),
        'raiseTime': report.raiseTime.isoformat(),
        'fallTime': report.fallTime.isoformat(),
    }


def get_analysis_context(analysis_id=None):
    analyses = list(
        Analysis.objects
        .prefetch_related('reports')
        .order_by('id')
    )
    requested_analysis = next(
        (analysis for analysis in analyses if str(analysis.id) == str(analysis_id)),
        None,
    )
    selected_analysis = requested_analysis if analysis_id else (analyses[0] if analyses else None)
    analysis_payload = [
        {
            'id': analysis.id,
            'title': analysis.title,
            'description': analysis.description,
            'reports': [serialize_report(report) for report in analysis.reports.all()],
        }
        for analysis in analyses
    ]
    return {
        'analyses': analyses,
        'analysis_payload': analysis_payload,
        'selected_analysis': selected_analysis,
        'selected_reports': list(selected_analysis.reports.all()) if selected_analysis else [],
        'selected_analysis_id': selected_analysis.id if selected_analysis else None,
        'requested_analysis': requested_analysis,
    }


def get_analysis_data(analysis_id=None):
    context = get_analysis_context(analysis_id)
    reports = context['selected_reports']
    report_data = [serialize_report(report) for report in reports]
    dataframe = pd.DataFrame(report_data) if report_data else pd.DataFrame()
    return context, reports, dataframe
def graph_data_analysis(df):

    if not df.empty:

        # ==========================================================
        # DESCRIPTION
        # ==========================================================

        description = pd.DataFrame({
            'Frequency': df['frequency'],
            'Frequency Min': df['frequencyMin'],
            'Frequency Max': df['frequencyMax'],
            'Frequency Avg': df['frequencyAvg'],

            'PRI': df['pri'],
            'PRI Min': df['priMin'],
            'PRI Max': df['priMax'],
            'PRI Avg': df['priAvg'],

            'PW': df['pw'],
            'PW Min': df['pwMin'],
            'PW Max': df['pwMax'],
            'PW Avg': df['pwAvg'],
        }).describe()

        description_columns = list(description.columns)

        description_rows = []

        for index, row in description.iterrows():
            description_rows.append({
                'name': index,
                'values': row.tolist()
            })


        # ==========================================================
        # 1. FREQUENCY MIN VS MAX
        # ==========================================================

        freq_min = df['frequencyMin'].tolist()
        freq_max = df['frequencyMax'].tolist()
        freq_interval_x = []
        freq_interval_y = []
        for index, (minimum, maximum) in enumerate(zip(freq_min, freq_max)):
            freq_interval_x.extend([minimum, maximum, None])
            freq_interval_y.extend([index, index, None])

        freq_plot = go.Scatter(x=freq_interval_x,y=freq_interval_y,mode='lines',line=dict(color='orange', width=3),hoverinfo='skip',showlegend=False,)
        freq_min_points = go.Scatter(x=freq_min,y=list(range(len(freq_min))),mode='markers',marker=dict(symbol='line-ns-open', size=13, color='black', line=dict(width=2)),name='Frequency Min',text=[f'Frequency Min: {value}' for value in freq_min],hoverinfo='text',)
        freq_max_points = go.Scatter(x=freq_max,y=list(range(len(freq_max))),mode='markers',marker=dict(symbol='line-ns-open', size=13, color='black', line=dict(width=2)),name='Frequency Max',text=[f'Frequency Max: {value}' for value in freq_max],hoverinfo='text',)
        freq_layout = go.Layout(title=dict(text='Frequency Min Vs Max',x=0.5,xanchor='center'),xaxis=dict(title='Frequency'),yaxis=dict(title='Record', showticklabels=False, autorange='reversed'),hovermode='closest')
        freq_fig = go.Figure(data=[freq_plot, freq_min_points, freq_max_points],layout=freq_layout)


        # ==========================================================
        # 2. PRI MIN VS MAX
        # ==========================================================

        pri_min = df['priMin'].tolist()
        pri_max = df['priMax'].tolist()
        pri_interval_x = []
        pri_interval_y = []
        for index, (minimum, maximum) in enumerate(zip(pri_min, pri_max)):
            pri_interval_x.extend([minimum, maximum, None])
            pri_interval_y.extend([index, index, None])

        pri_plot = go.Scatter( x=pri_interval_x, y=pri_interval_y, mode='lines', line=dict(color='blue', width=3), hoverinfo='skip', showlegend=False,)
        pri_min_points = go.Scatter(x=pri_min,y=list(range(len(pri_min))),mode='markers',marker=dict(symbol='line-ns-open', size=13, color='black', line=dict(width=2)),name='PRI Min',text=[f'PRI Min: {value}' for value in pri_min],hoverinfo='text',)
        pri_max_points = go.Scatter(x=pri_max,y=list(range(len(pri_max))),mode='markers',marker=dict(symbol='line-ns-open', size=13, color='black', line=dict(width=2)),name='PRI Max',text=[f'PRI Max: {value}' for value in pri_max],hoverinfo='text',)
        pri_layout = go.Layout(title=dict(text='PRI Min Vs Max',x=0.5,xanchor='center'),xaxis=dict(title='PRI'),yaxis=dict(title='Record', showticklabels=False, autorange='reversed'),hovermode='closest')
        pri_fig = go.Figure(data=[pri_plot, pri_min_points, pri_max_points],layout=pri_layout)


        # ==========================================================
        # 3. PW MIN VS MAX
        # ==========================================================

        pw_min = df['pwMin'].tolist()
        pw_max = df['pwMax'].tolist()
        pw_interval_x = []
        pw_interval_y = []
        for index, (minimum, maximum) in enumerate(zip(pw_min, pw_max)):
            pw_interval_x.extend([minimum, maximum, None])
            pw_interval_y.extend([index, index, None])

        pw_plot = go.Scatter( x=pw_interval_x, y=pw_interval_y, mode='lines', line=dict(color='green', width=3), hoverinfo='skip', showlegend=False,)
        pw_min_points = go.Scatter(x=pw_min,y=list(range(len(pw_min))),mode='markers',marker=dict(symbol='line-ns-open', size=13, color='black', line=dict(width=2)),name='PW Min',text=[f'PW Min: {value}' for value in pw_min],hoverinfo='text',)
        pw_max_points = go.Scatter(x=pw_max,y=list(range(len(pw_max))),mode='markers',marker=dict(symbol='line-ns-open', size=13, color='black', line=dict(width=2)),name='PW Max',text=[f'PW Max: {value}' for value in pw_max],hoverinfo='text',)
        pw_layout = go.Layout(title=dict( text='PW Min Vs Max', x=0.5, xanchor='center'),xaxis=dict(title='PW'),yaxis=dict(title='Record', showticklabels=False, autorange='reversed'),hovermode='closest')
        pw_fig = go.Figure(data=[pw_plot, pw_min_points, pw_max_points],layout=pw_layout)


        # ==========================================================
        # 4. FREQUENCY VS PRI
        # ==========================================================

        freq_vs_pri_plot = go.Scattergl(x=df['frequency'].tolist(),y=df['pri'].tolist(),mode='markers',marker=dict(symbol=17,size=9,opacity=0.8,color='red'),hoverinfo='text',text=['Frequency : ' + str(row['frequency']) +'<br>PRI : ' + str(row['pri'])for _, row in df.iterrows()])
        freq_vs_pri_layout = go.Layout( title=dict(text='Frequency Vs PRI',x=0.5,xanchor='center'), xaxis=dict(title='Frequency'), yaxis=dict(title='PRI'), hovermode='closest')
        freq_vs_pri_fig = go.Figure(data=[freq_vs_pri_plot],layout=freq_vs_pri_layout)


        # ==========================================================
        # 5. PRI VS PW
        # ==========================================================

        pri_vs_pw_plot = go.Scattergl(x=df['pri'].tolist(),y=df['pw'].tolist(),mode='markers',marker=dict(symbol=17,size=9,opacity=0.8,color='blue'),line=dict(width=0),hoverinfo='text',text=['PRI : ' + str(row['pri']) +'<br>PW : ' + str(row['pw'])for _, row in df.iterrows()])
        pri_vs_pw_layout = go.Layout(title=dict(text='PRI Vs PW',x=0.5,xanchor='center'),xaxis=dict(title='PRI'),yaxis=dict(title='PW'),hovermode='closest',showlegend=False)
        pri_vs_pw_fig = go.Figure(data=[pri_vs_pw_plot],layout=pri_vs_pw_layout)


        # ==========================================================
        # 6. PW VS FREQUENCY
        # ==========================================================
        pw_vs_freq_plot = go.Scattergl(x=df['pw'].tolist(),y=df['frequency'].tolist(),mode='markers',marker=dict(symbol=17,size=9,opacity=0.8,color='orange'),line=dict(width=0),hoverinfo='text',text=['PW : ' + str(row['pw']) +'<br>Frequency : ' + str(row['frequency'])for _, row in df.iterrows()])
        pw_vs_freq_layout = go.Layout(title=dict(text='PW Vs Frequency',x=0.5,xanchor='center'),xaxis=dict( title='PW'),yaxis=dict(title='Frequency'),hovermode='closest',showlegend=False)
        pw_vs_freq_fig = go.Figure(data=[pw_vs_freq_plot],layout=pw_vs_freq_layout)


        # ==========================================================
        # 7. TIME VS FREQUENCY
        # ==========================================================

        time_vs_freq_plot = go.Scattergl( x=df['raiseTime'].tolist(), y=df['frequency'].tolist(), mode='markers', marker=dict(symbol=17,size=9,opacity=0.8,color='purple'), line=dict(width=0), hoverinfo='text', text=['Time : ' +str(row['raiseTime']) +'<br>Frequency : ' +str(row['frequency'])for _, row in df.iterrows()])
        time_vs_freq_layout = go.Layout(title=dict(text='Time Vs Frequency',x=0.5,xanchor='center'),xaxis=dict(title='Time',type='date'),yaxis=dict(title='Frequency'),hovermode='closest',showlegend=False)
        time_vs_freq_fig = go.Figure(data=[time_vs_freq_plot],layout=time_vs_freq_layout)


        # ==========================================================
        # 8. TIME VS PRI
        # ==========================================================

        time_vs_pri_plot = go.Scattergl(x=df['raiseTime'].tolist(),y=df['pri'].tolist(),mode='markers',marker=dict(symbol=17,size=9,opacity=0.8,color='brown'),line=dict(width=0),hoverinfo='text',text=['Time : ' +str(row['raiseTime']) +'<br>PRI : ' +str(row['pri'])for _, row in df.iterrows()])
        time_vs_pri_layout = go.Layout(title=dict(text='Time Vs PRI',x=0.5,xanchor='center'), xaxis=dict(title='Time',type='date'), yaxis=dict(title='PRI'), hovermode='closest', showlegend=False)
        time_vs_pri_fig = go.Figure(data=[time_vs_pri_plot],layout=time_vs_pri_layout)


        # ==========================================================
        # 9. TIME VS PW
        # ==========================================================

        time_vs_pw_plot = go.Scattergl( x=df['raiseTime'].tolist(), y=df['pw'].tolist(), mode='markers', marker=dict(symbol=17,size=9,opacity=0.8,color='black'), line=dict(width=0), hoverinfo='text', text=['Time : ' +str(row['raiseTime']) +'<br>PW : ' +str(row['pw'])for _, row in df.iterrows() ])
        time_vs_pw_layout = go.Layout(title=dict(text='Time Vs PW',x=0.5,xanchor='center'),xaxis=dict(title='Time',type='date'),yaxis=dict(title='PW'),hovermode='closest',showlegend=False)
        time_vs_pw_fig = go.Figure(data=[time_vs_pw_plot],layout=time_vs_pw_layout)


        # ==========================================================
        # 10. 3D FREQUENCY VS PRI VS PW
        # ==========================================================

        frequency_pri_pw_plot = go.Scatter3d(x=df['frequency'].tolist(),y=df['pri'].tolist(),z=df['pw'].tolist(),name='Frequency Vs PRI Vs PW',mode='markers',marker=dict(size=6,opacity=0.8,color=df['frequency'].tolist(),colorscale='Viridis'),hoverinfo='text',text=['Frequency : ' + str(row['frequency']) +'<br>PRI : ' + str(row['pri']) +'<br>PW : ' + str(row['pw'])for _, row in df.iterrows()],)

        frequency_pri_pw_fig = go.Figure(data=[frequency_pri_pw_plot],layout=go.Layout(title=dict(text='Frequency Vs PRI Vs PW',x=0.5,xanchor='center'),scene=dict(xaxis=dict(title='Frequency'),yaxis=dict(title='PRI'),zaxis=dict(title='PW')),hovermode='closest'))
        


        # ==========================================================
        # CONVERT GRAPHS TO HTML
        # ==========================================================

        divFreqMinMax = opy.plot(freq_fig,auto_open=False,output_type='div')

        divPRIMinMax = opy.plot(pri_fig,auto_open=False,output_type='div')

        divPWMinMax = opy.plot(pw_fig,auto_open=False,output_type='div')

        divFreqVsPri = opy.plot(freq_vs_pri_fig,auto_open=False,output_type='div')

        divPriVsPW = opy.plot(pri_vs_pw_fig,auto_open=False,output_type='div')

        divPWVsFreq = opy.plot(pw_vs_freq_fig,auto_open=False,output_type='div')

        divTimeVsFreq = opy.plot(time_vs_freq_fig,auto_open=False,output_type='div')

        divTimeVsPri = opy.plot(time_vs_pri_fig,auto_open=False,output_type='div')

        divTimeVsPW = opy.plot(time_vs_pw_fig,auto_open=False,output_type='div')

        div3D = opy.plot(frequency_pri_pw_fig,auto_open=False,output_type='div')

    else:

        description_columns = []
        description_rows = []

        divFreqMinMax = ''
        divPRIMinMax = ''
        divPWMinMax = ''

        divFreqVsPri = ''
        divPriVsPW = ''
        divPWVsFreq = ''

        divTimeVsFreq = ''
        divTimeVsPri = ''
        divTimeVsPW = ''

        div3D = ''


    # ==========================================================
    # RETURN ALL VALUES
    # ==========================================================

    return (
        description_columns,
        description_rows,

        divFreqMinMax,
        divPRIMinMax,
        divPWMinMax,

        divFreqVsPri,
        divPriVsPW,
        divPWVsFreq,

        divTimeVsFreq,
        divTimeVsPri,
        divTimeVsPW,

        div3D
    )




class StaticAnalysis(View):
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        
        selected_id = kwargs.get('analysis_id')
        context_data, _, df = get_analysis_data(selected_id)
        analyses = context_data['analyses']
        analysis_payload = context_data['analysis_payload']
        graph_data_analysis(df) 
        (description_columns,description_rows,divFreqMinMax,divPRIMinMax,divPWMinMax,divFreqVsPri,divPriVsPW,divPWVsFreq,divTimeVsFreq,divTimeVsPri,divTimeVsPW,div3D) = graph_data_analysis(df)
        # import pdb;pdb.set_trace()
        context = {
            'analyses': analyses,
            'analysis_payload': analysis_payload,
            'description_columns': description_columns,
            'description_rows': description_rows,
            'divFreqMinMax': divFreqMinMax,
            'divPRIMinMax': divPRIMinMax,
            'divPWMinMax': divPWMinMax,
            'divFreqVsPri': divFreqVsPri,
            'divPWVsPRI': divPriVsPW,
            'divPWVsFreq': divPWVsFreq,
            "divTimeVsFreq": divTimeVsFreq,
            "divTimeVsPri": divTimeVsPri,
            "divTimeVsPW": divTimeVsPW,
            'div3D': div3D,
            'selected_analysis_id': (
                int(selected_id)
                if selected_id

                else context_data['selected_analysis_id']
            ),
        }

        return render(
            request,
            'staticAnalysis.html',
            context
        )
    def post(self, request, *args, **kwargs):
        try:
            data_dict = json.loads(request.body.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)
        analysis_id = data_dict.get('analysis_id') or kwargs.get('analysis_id')
        if not analysis_id:
            return JsonResponse({'success': False, 'message': 'analysis_id is required.'}, status=400)

        context_data, df = get_analysis_data(analysis_id)
        if not context_data['requested_analysis']:
            return JsonResponse({'success': False, 'message': 'Analysis was not found.'}, status=404)

        analysis_payload = context_data['analysis_payload']
        (description_columns,description_rows,divFreqMinMax,divPRIMinMax,divPWMinMax,divFreqVsPri,divPriVsPW,divPWVsFreq,divTimeVsFreq,divTimeVsPri,divTimeVsPW,div3D) = graph_data_analysis(df)


        try:
            return JsonResponse({
                'success': True,
                'analysis_id': int(analysis_id),
                'analysis_payload': analysis_payload,
                'description_columns': description_columns,
                'description_rows': description_rows,
                'divFreqMinMax': divFreqMinMax,
                'divPRIMinMax': divPRIMinMax,
                'divPWMinMax': divPWMinMax,
                'divFreqVsPri': divFreqVsPri,
                'divPRIVsPW': divPriVsPW,
                'divPWVsFreq': divPWVsFreq,
                'divTimeVsFreq': divTimeVsFreq,
                'divTimeVsPri': divTimeVsPri,
                'divTimeVsPW': divTimeVsPW,
                'div3D': div3D,  
            })

        except ValueError as error:
            return JsonResponse({'success': False, 'message': str(error)}, status=400)



