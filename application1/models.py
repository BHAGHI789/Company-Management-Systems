import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models  # type: ignore

# Create your models here.


class User(AbstractUser):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(verbose_name="Email", unique=True)
    phoneNumber = models.CharField(
        verbose_name="Phone Number", max_length=15, blank=True, null=True
    )
    role = models.ForeignKey(
        "Roles",
        verbose_name="Role",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users",
    )
    createdDate = models.DateTimeField(verbose_name="Created Date", auto_now_add=True)
    updatedDate = models.DateTimeField(verbose_name="Updated Date", auto_now=True)

    def __str__(self):
        return self.username


class Department(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.CharField(
        verbose_name="Department ", max_length=100, unique=True, blank=False, null=False
    )
    description = models.TextField(blank=True)
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="departments_created",
    )
    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="departments_updated",
    )
    createdDate = models.DateTimeField(verbose_name="Created Date", auto_now_add=True)
    updatedDate = models.DateTimeField(verbose_name="Updated Date", auto_now=True)

    def __str__(self):
        return self.department


class Designation(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    designation = models.CharField(
        verbose_name="Designation ", max_length=100, unique=True
    )
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        Department, verbose_name="Department", on_delete=models.CASCADE
    )
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="designation_created",
    )
    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="designation_updated",
    )
    createdDate = models.DateTimeField(verbose_name="Created Date", auto_now_add=True)
    updatedDate = models.DateTimeField(verbose_name="Updated Date", auto_now=True)

    def __str__(self):
        return self.designation


class Roles(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    roleName = models.CharField(verbose_name="Role Name", max_length=100, unique=True)
    description = models.TextField(blank=True)
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roles_created",
    )
    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roles_updated",
    )
    createdDate = models.DateTimeField(verbose_name="Created Date", auto_now_add=True)
    updatedDate = models.DateTimeField(verbose_name="Updated Date", auto_now=True)

    def __str__(self):
        return self.roleName


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_code = models.CharField(max_length=50, unique=True)
    company_name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255, blank=True, null=True)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    website_name = models.CharField(max_length=255, blank=True, null=True)
    website_url = models.URLField(max_length=500, blank=True, null=True)
    domain_name = models.CharField(max_length=255, unique=True, blank=True, null=True)
    subdomain = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    industry = models.CharField(max_length=150, blank=True, null=True)
    company_size = models.CharField(max_length=50, blank=True, null=True)
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    alternate_phone = models.CharField(max_length=20, blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    logo = models.ImageField(upload_to="companies/logos/", blank=True, null=True)
    favicon = models.ImageField(upload_to="companies/favicons/", blank=True, null=True)
    primary_color = models.CharField(max_length=20, default="#1976D2")
    secondary_color = models.CharField(max_length=20, default="#FFFFFF")
    linkedin_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    subscription_plan = models.CharField(max_length=50, default="FREE")
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "companies"


class Employees(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, verbose_name="User", on_delete=models.CASCADE, related_name="employee"
    )
    employeeName = models.CharField(
        verbose_name="Employee Name ",
        max_length=100,
        blank=False,
        unique=True,
        null=False,
    )
    employeeID = models.CharField(
        verbose_name="Employee ID", max_length=100, blank=False, unique=True, null=False
    )
    employeeEmail = models.EmailField(verbose_name="Employee Email", unique=True)
    employeePanNumber = models.CharField(
        verbose_name="Employee PanCard Number",
        max_length=100,
        blank=False,
        unique=True,
        null=False,
    )
    employeeStatus = models.CharField(
        verbose_name="Employee Status",
        max_length=20,
        choices=[
            ("Active", "Active"),
            ("Pending", "Pending"),
            ("Terminated", "Terminated"),
        ],
        default="Active",
    )
    reportingManager = models.ForeignKey(
        "self",
        verbose_name="Reporting Manager",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reportingEmployees",
    )
    department = models.ForeignKey(
        Department, verbose_name="Department", on_delete=models.CASCADE
    )
    designation = models.ForeignKey(
        Designation, verbose_name="Designation", on_delete=models.CASCADE
    )
    role = models.ForeignKey(Roles, verbose_name="Roles", on_delete=models.CASCADE)
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees_created",
    )
    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees_updated",
    )
    createdDate = models.DateTimeField(verbose_name="Created Date", auto_now_add=True)
    updatedDate = models.DateTimeField(verbose_name="Updated Date", auto_now=True)

    def __str__(self):
        return self.employeeName


class OTPValues(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(verbose_name="Email", unique=True)
    otp = models.CharField(verbose_name="OTP", max_length=6)
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="otp_created",
    )

    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="otp_updated",
    )
    createdDate = models.DateTimeField(verbose_name="Created Date", auto_now_add=True)
    updatedDate = models.DateTimeField(verbose_name="Updated Date", auto_now=True)

    def __str__(self):
        return self.email


class EmployeeSalary(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )
    STATUS = [
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
        ("TERMINATED", "Terminated"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        Employees,
        verbose_name="Employee",
        on_delete=models.PROTECT,
        related_name="salary_details",
    )
    effectiveFrom = models.DateField(verbose_name="Effective From")
    effectiveTo = models.DateField(verbose_name="Effective To", null=True, blank=True)
    basicSalary = models.DecimalField(
        verbose_name="Basic Salary", max_digits=14, decimal_places=2, default=0
    )
    hra = models.DecimalField(
        verbose_name="HRA", max_digits=14, decimal_places=2, default=0
    )
    conveyanceAllowance = models.DecimalField(
        verbose_name="Conveyance Allowance", max_digits=14, decimal_places=2, default=0
    )
    medicalAllowance = models.DecimalField(
        verbose_name="Medical Allowance", max_digits=14, decimal_places=2, default=0
    )
    otherAllowance = models.DecimalField(
        verbose_name="Other Allowance", max_digits=14, decimal_places=2, default=0
    )
    bonus = models.DecimalField(
        verbose_name="Bonus", max_digits=14, decimal_places=2, default=0
    )
    grossSalary = models.DecimalField(
        verbose_name="Gross Salary", max_digits=14, decimal_places=2, default=0
    )
    pfDeduction = models.DecimalField(
        verbose_name="PF Deduction", max_digits=14, decimal_places=2, default=0
    )
    professionalTax = models.DecimalField(
        verbose_name="Professional Tax", max_digits=14, decimal_places=2, default=0
    )
    incomeTax = models.DecimalField(
        verbose_name="Income Tax", max_digits=14, decimal_places=2, default=0
    )
    otherDeduction = models.DecimalField(
        verbose_name="Other Deduction", max_digits=14, decimal_places=2, default=0
    )
    totalDeduction = models.DecimalField(
        verbose_name="Total Deduction", max_digits=14, decimal_places=2, default=0
    )
    netSalary = models.DecimalField(
        verbose_name="Net Salary", max_digits=14, decimal_places=2, default=0
    )
    employeeStatus = models.CharField(
        verbose_name="Employee Status", max_length=10, choices=STATUS, default="ACTIVE"
    )
    notes = models.TextField(verbose_name="Notes", blank=True)
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_salaries_created",
    )
    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_salaries_updated",
    )
    createdDate = models.DateTimeField(verbose_name="Created Date", auto_now_add=True)
    updatedDate = models.DateTimeField(verbose_name="Updated Date", auto_now=True)

    def save(self, *args, **kwargs):
        self.grossSalary = (
            self.basicSalary
            + self.hra
            + self.conveyanceAllowance
            + self.medicalAllowance
            + self.otherAllowance
            + self.bonus
        )
        self.totalDeduction = (
            self.pfDeduction
            + self.professionalTax
            + self.incomeTax
            + self.otherDeduction
        )
        self.netSalary = self.grossSalary - self.totalDeduction
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.employeeID} - {self.netSalary}"


def employee_image_path(instance, filename):
    return f"employees/{instance.employee.employeeID}/images/{filename}"


def employee_file_path(instance, filename):
    return f"employees/{instance.employee.employeeID}/files/{filename}"


class EmployeeImage(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        Employees,
        verbose_name="Employees",
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(
        verbose_name="Employee Image", upload_to=employee_image_path
    )
    imageName = models.CharField(verbose_name="Image Name", max_length=255, blank=True)
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employeeImage_created",
    )
    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employeeImage_updated",
    )
    createdDate = models.DateTimeField(verbose_name="Created Date", auto_now_add=True)
    updatedDate = models.DateTimeField(verbose_name="Updated Date", auto_now=True)

    def __str__(self):
        return self.imageName


class EmployeeFile(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        Employees,
        verbose_name="Employees",
        on_delete=models.CASCADE,
        related_name="files",
    )
    file = models.FileField(verbose_name="Employee Image", upload_to=employee_file_path)
    fileName = models.CharField(verbose_name="Image Name", max_length=255, blank=True)
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employeeFile_created",
    )
    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employeeFile_updated",
    )
    createdDate = models.DateTimeField(verbose_name="Created Date", auto_now_add=True)
    updatedDate = models.DateTimeField(verbose_name="Updated Date", auto_now=True)

    def __str__(self):
        return self.fileName


class Project(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    PROJECT_STATUS_CHOICES = [
        ("PLANNED", "Planned"),
        ("IN_PROGRESS", "In Progress"),
        ("ON_HOLD", "On Hold"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    projectName = models.CharField(
        verbose_name="Project Name", max_length=200, unique=True
    )
    projectCode = models.CharField(
        verbose_name="Project Code", max_length=50, unique=True
    )
    description = models.TextField(verbose_name="Project Description", blank=True)
    startDate = models.DateField(verbose_name="Start Date")
    endDate = models.DateField(verbose_name="End Date", null=True, blank=True)
    status = models.CharField(
        verbose_name="Project Status",
        max_length=20,
        choices=PROJECT_STATUS_CHOICES,
        default="PLANNED",
    )
    director = models.ForeignKey(
        Employees,
        verbose_name="Project Director",
        on_delete=models.PROTECT,
        related_name="directed_projects",
    )
    projectManager = models.ForeignKey(
        Employees,
        verbose_name="Project Manager",
        on_delete=models.PROTECT,
        related_name="managed_projects",
    )
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects_created",
    )
    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects_updated",
    )
    createdDate = models.DateTimeField(verbose_name="Created Date", auto_now_add=True)
    updatedDate = models.DateTimeField(verbose_name="Updated Date", auto_now=True)

    def __str__(self):
        return f"{self.projectCode} - {self.projectName}"


class ProjectTeam(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        verbose_name="Project",
        on_delete=models.CASCADE,
        related_name="team_members",
    )
    employee = models.ForeignKey(
        Employees,
        verbose_name="Employee",
        on_delete=models.PROTECT,
        related_name="project_assignments",
    )
    projectRole = models.ForeignKey(
        Roles,
        verbose_name="Project Role",
        on_delete=models.PROTECT,
        related_name="project_team_members",
    )
    reportingTo = models.ForeignKey(
        "self",
        verbose_name="Reporting To",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reporting_members",
    )
    joinedDate = models.DateField(verbose_name="Joined Date", auto_now_add=True)
    isActive = models.BooleanField(verbose_name="Active", default=True)
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_team_created",
    )
    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_team_updated",
    )
    createdDate = models.DateTimeField(verbose_name="Created Date", auto_now_add=True)
    updatedDate = models.DateTimeField(verbose_name="Updated Date", auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "employee"], name="unique_employee_project"
            )
        ]


class WorkItemType(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name="Work Item Type", max_length=100, unique=True)
    description = models.TextField(verbose_name="Description", blank=True)
    isActive = models.BooleanField(verbose_name="Active", default=True)
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_item_types_created",
    )
    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_item_types_updated",
    )
    createdDate = models.DateTimeField(verbose_name="Created Date", auto_now_add=True)
    updatedDate = models.DateTimeField(verbose_name="Updated Date", auto_now=True)

    def __str__(self):
        return self.name


class ProjectSprint(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    SPRINT_STATUS_CHOICES = [
        ("PLANNED", "Planned"),
        ("ACTIVE", "Active"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        verbose_name="Project",
        on_delete=models.CASCADE,
        related_name="sprints",
    )
    sprintName = models.CharField(verbose_name="Sprint Name", max_length=100)
    sprintCode = models.CharField(verbose_name="Sprint Code", max_length=50)
    sprintGoal = models.TextField(verbose_name="Sprint Goal", blank=True)
    startDate = models.DateField(verbose_name="Start Date")
    storyPoints = models.DecimalField(
        verbose_name="Story Points", max_digits=8, decimal_places=2, default=0
    )
    capacityHours = models.DecimalField(
        verbose_name="Capacity Hours",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    endDate = models.DateField(verbose_name="End Date")
    sprintStatus = models.CharField(
        verbose_name="Sprint Status",
        max_length=20,
        choices=SPRINT_STATUS_CHOICES,
        default="PLANNED",
    )
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sprints_created",
    )
    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sprints_updated",
    )
    createdDate = models.DateTimeField(verbose_name="Created Date", auto_now_add=True)
    updatedDate = models.DateTimeField(verbose_name="Updated Date", auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "sprintCode"], name="unique_project_sprint_code"
            )
        ]
        ordering = ["startDate"]

    def __str__(self):
        return f"{self.project.projectCode} - {self.sprintName}"


class ProjectTask(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    TASK_STATUS_CHOICES = [
        ("New", "New"),
        ("IN_PROGRESS", "In Progress"),
        ("TESTING", "Testing"),
        ("ON_HOLD", "On Hold"),
        ("CANCELLED", "Cancelled"),
        ("RESOLVED", "Resolved"),
        ("COMPLETED", "Completed"),
    ]
    TASK_PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, verbose_name="Project", on_delete=models.CASCADE, related_name="tasks"
    )
    employee = models.ForeignKey(
        Employees,
        verbose_name="Assigned Employee",
        on_delete=models.PROTECT,
        related_name="project_tasks",
    )
    taskName = models.CharField(verbose_name="Task Name", max_length=200)
    taskDescription = models.TextField(verbose_name="Task Description", blank=True)
    taskStatus = models.CharField(
        verbose_name="Task Status",
        max_length=20,
        choices=TASK_STATUS_CHOICES,
        default="New",
    )
    priority = models.CharField(
        verbose_name="Priority",
        max_length=20,
        choices=TASK_PRIORITY_CHOICES,
        default="MEDIUM",
    )
    developedBy = models.ForeignKey(
        Employees,
        verbose_name="Developed By",
        on_delete=models.PROTECT,
        related_name="tasks_developed",
        null=True,
        blank=True,
    )
    reviewedBy = models.ForeignKey(
        Employees,
        verbose_name="Reviewed By",
        on_delete=models.PROTECT,
        related_name="tasks_reviewed",
        null=True,
        blank=True,
    )
    testedBy = models.ForeignKey(
        Employees,
        verbose_name="Tested By",
        on_delete=models.PROTECT,
        related_name="tasks_tested",
        null=True,
        blank=True,
    )
    closedBy = models.ForeignKey(
        Employees,
        verbose_name="Closed By",
        on_delete=models.PROTECT,
        related_name="tasks_closed",
        null=True,
        blank=True,
    )
    sprintStartedDate = models.DateTimeField(
        verbose_name="Sprint Started Date", auto_now_add=True
    )
    sprintEndDate = models.DateTimeField(
        verbose_name="Sprint End Date", null=True, blank=True
    )
    sprintCount = models.IntegerField(verbose_name="Sprint Count", default=0)
    sprint = models.ForeignKey(
        ProjectSprint,
        verbose_name="Sprint",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    startDate = models.DateField(verbose_name="Start Date")
    dueDate = models.DateField(verbose_name="Due Date", null=True, blank=True)
    workItemType = models.ForeignKey(
        WorkItemType,
        verbose_name="Work Item Type",
        on_delete=models.PROTECT,
        related_name="project_tasks",
    )
    completedDate = models.DateField(
        verbose_name="Completed Date", null=True, blank=True
    )
    assignedBy = models.ForeignKey(
        Employees,
        verbose_name="Assigned By",
        on_delete=models.PROTECT,
        related_name="assigned_project_tasks",
    )
    estimatedHours = models.DecimalField(
        verbose_name="Estimated Hours",
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )
    actualHours = models.DecimalField(
        verbose_name="Actual Hours",
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_tasks_created",
    )
    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_tasks_updated",
    )
    createdDate = models.DateTimeField(verbose_name="Created Date", auto_now_add=True)
    updatedDate = models.DateTimeField(verbose_name="Updated Date", auto_now=True)

    def __str__(self):
        return f"{self.project.projectCode} - {self.taskName}"


class TaskHistory(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        ProjectTask,
        verbose_name="Task",
        on_delete=models.CASCADE,
        related_name="history",
    )
    employee = models.ForeignKey(
        Employees,
        verbose_name="Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_history",
    )
    oldStatus = models.CharField(verbose_name="Old Status", max_length=30, blank=True)
    newStatus = models.CharField(verbose_name="New Status", max_length=30, blank=True)
    action = models.CharField(verbose_name="Action", max_length=200)
    comments = models.TextField(verbose_name="Comments", blank=True)
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_history_created",
    )
    createdDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.taskName} - {self.action}"


class ProjectTaskAttachment(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    ATTACHMENT_TYPE_CHOICES = [
        ("IMAGE", "Image"),
        ("FILE", "File"),
        ("VIDEO", "Video"),
        ("LINK", "Link"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        ProjectTask,
        verbose_name="Project Task",
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    attachmentType = models.CharField(
        verbose_name="Attachment Type", max_length=20, choices=ATTACHMENT_TYPE_CHOICES
    )
    file = models.FileField(
        verbose_name="File", upload_to="project_tasks/files/", null=True, blank=True
    )
    link = models.URLField(
        verbose_name="External Link", max_length=1000, null=True, blank=True
    )
    attachmentName = models.CharField(
        verbose_name="Attachment Name", max_length=255, blank=True
    )
    description = models.TextField(verbose_name="Attachment Description", blank=True)
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_attachments_created",
    )
    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_attachments_updated",
    )
    createdDate = models.DateTimeField(verbose_name="Created Date", auto_now_add=True)
    updatedDate = models.DateTimeField(verbose_name="Updated Date", auto_now=True)

    def __str__(self):
        return f"{self.task.taskName} - {self.attachmentName}"


class ProjectBudget(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    BUDGET_STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("APPROVED", "Approved"),
        ("ACTIVE", "Active"),
        ("CLOSED", "Closed"),
        ("CANCELLED", "Cancelled"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.OneToOneField(
        Project, verbose_name="Project", on_delete=models.CASCADE, related_name="budget"
    )
    budgetName = models.CharField(verbose_name="Budget Name", max_length=200)
    totalBudget = models.DecimalField(
        verbose_name="Total Budget", max_digits=14, decimal_places=2, default=0
    )
    approvedBudget = models.DecimalField(
        verbose_name="Approved Budget", max_digits=14, decimal_places=2, default=0
    )
    budgetStatus = models.CharField(
        verbose_name="Budget Status",
        max_length=20,
        choices=BUDGET_STATUS_CHOICES,
        default="DRAFT",
    )
    startDate = models.DateField(verbose_name="Start Date")
    endDate = models.DateField(verbose_name="End Date", null=True, blank=True)
    notes = models.TextField(verbose_name="Notes", blank=True)
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_budgets_created",
    )
    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_budgets_updated",
    )
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.projectCode} - {self.budgetName}"


class ProjectExpense(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    EXPENSE_CATEGORY_CHOICES = [
        ("INFRASTRUCTURE", "Infrastructure"),
        ("SOFTWARE", "Software"),
        ("HARDWARE", "Hardware"),
        ("TRAVEL", "Travel"),
        ("TRAINING", "Training"),
        ("LICENSE", "License"),
        ("OFFICE", "Office"),
        ("OTHER", "Other"),
    ]
    EXPENSE_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("PAID", "Paid"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        verbose_name="Project",
        on_delete=models.CASCADE,
        related_name="project_details",
    )
    budget = models.ForeignKey(
        ProjectBudget,
        verbose_name="Budget",
        on_delete=models.PROTECT,
        related_name="project_budget",
    )
    expenseTitle = models.CharField(verbose_name="Expense Title", max_length=200)
    expenseCategory = models.CharField(
        verbose_name="Expense Category", max_length=30, choices=EXPENSE_CATEGORY_CHOICES
    )
    description = models.TextField(verbose_name="Description", blank=True)
    expenseDate = models.DateField(verbose_name="Expense Date")
    amount = models.DecimalField(verbose_name="Amount", max_digits=14, decimal_places=2)
    expenseStatus = models.CharField(
        verbose_name="Expense Status",
        max_length=20,
        choices=EXPENSE_STATUS_CHOICES,
        default="PENDING",
    )
    vendorName = models.CharField(
        verbose_name="Vendor Name", max_length=200, blank=True
    )
    invoiceNumber = models.CharField(
        verbose_name="Invoice Number", max_length=100, blank=True
    )
    approvedBy = models.ForeignKey(
        Employees,
        verbose_name="Approved By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_project_expenses",
    )
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_expenses_created",
    )
    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_expenses_updated",
    )
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.projectCode} - {self.expenseTitle}"


class ProjectEmployeeCost(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    COST_STATUS_CHOICES = [
        ("ESTIMATED", "Estimated"),
        ("CALCULATED", "Calculated"),
        ("APPROVED", "Approved"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        verbose_name="Project",
        on_delete=models.CASCADE,
        related_name="employee_costs",
    )
    sprint = models.ForeignKey(
        ProjectSprint,
        verbose_name="Sprint",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_costs",
    )
    task = models.ForeignKey(
        ProjectTask,
        verbose_name="Task",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_costs",
    )
    employee = models.ForeignKey(
        Employees,
        verbose_name="Employee",
        on_delete=models.PROTECT,
        related_name="project_employee_costs",
    )
    startDate = models.DateField(verbose_name="Start Date")
    endDate = models.DateField(verbose_name="End Date")
    workingHours = models.DecimalField(
        verbose_name="Working Hours", max_digits=8, decimal_places=2, default=0
    )
    hourlyRate = models.DecimalField(
        verbose_name="Hourly Rate", max_digits=10, decimal_places=2, default=0
    )
    totalCost = models.DecimalField(
        verbose_name="Total Cost", max_digits=14, decimal_places=2, default=0
    )
    costStatus = models.CharField(
        verbose_name="Cost Status",
        max_length=20,
        choices=COST_STATUS_CHOICES,
        default="ESTIMATED",
    )
    notes = models.TextField(verbose_name="Notes", blank=True)
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_costs_created",
    )
    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_costs_updated",
    )
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.totalCost = self.workingHours * self.hourlyRate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project.projectCode} - " f"{self.employee.employeeID}"


class ClientBilling(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    BILLING_STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("SENT", "Sent"),
        ("PARTIALLY_PAID", "Partially Paid"),
        ("PAID", "Paid"),
        ("OVERDUE", "Overdue"),
        ("CANCELLED", "Cancelled"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        verbose_name="Project",
        on_delete=models.PROTECT,
        related_name="client_billings",
    )
    invoiceNumber = models.CharField(
        verbose_name="Invoice Number", max_length=100, unique=True
    )
    invoiceDate = models.DateField(verbose_name="Invoice Date")
    dueDate = models.DateField(verbose_name="Due Date")
    subtotal = models.DecimalField(
        verbose_name="Subtotal", max_digits=14, decimal_places=2, default=0
    )
    taxAmount = models.DecimalField(
        verbose_name="Tax Amount", max_digits=14, decimal_places=2, default=0
    )
    discountAmount = models.DecimalField(
        verbose_name="Discount Amount", max_digits=14, decimal_places=2, default=0
    )
    totalAmount = models.DecimalField(
        verbose_name="Total Amount", max_digits=14, decimal_places=2, default=0
    )
    paidAmount = models.DecimalField(
        verbose_name="Paid Amount", max_digits=14, decimal_places=2, default=0
    )
    billingStatus = models.CharField(
        verbose_name="Billing Status",
        max_length=20,
        choices=BILLING_STATUS_CHOICES,
        default="DRAFT",
    )
    notes = models.TextField(verbose_name="Notes", blank=True)
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="client_billings_created",
    )
    updatedBy = models.ForeignKey(
        User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="client_billings_updated",
    )
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(auto_now=True)

    @property
    def outstandingAmount(self):
        return self.totalAmount - self.paidAmount

    def __str__(self):
        return self.invoiceNumber


class ClientBillingItem(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    billing = models.ForeignKey(
        ClientBilling,
        verbose_name="Billing",
        on_delete=models.CASCADE,
        related_name="billing_items",
    )
    task = models.ForeignKey(
        ProjectTask,
        verbose_name="Task",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_task",
    )
    description = models.CharField(verbose_name="Description", max_length=300)
    quantity = models.DecimalField(
        verbose_name="Quantity", max_digits=10, decimal_places=2, default=1
    )
    unitPrice = models.DecimalField(
        verbose_name="Unit Price", max_digits=14, decimal_places=2, default=0
    )
    amount = models.DecimalField(
        verbose_name="Amount", max_digits=14, decimal_places=2, default=0
    )
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.unitPrice
        super().save(*args, **kwargs)

    def __str__(self):
        return self.description


class ClientPayment(models.Model):
    company = models.ForeignKey(
        "Company",
        verbose_name="Company",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(class)s_records",
    )

    PAYMENT_METHOD_CHOICES = [
        ("BANK_TRANSFER", "Bank Transfer"),
        ("UPI", "UPI"),
        ("CREDIT_CARD", "Credit Card"),
        ("CHEQUE", "Cheque"),
        ("CASH", "Cash"),
        ("OTHER", "Other"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    billing = models.ForeignKey(
        ClientBilling,
        verbose_name="Billing",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    paymentDate = models.DateField(verbose_name="Payment Date")
    amount = models.DecimalField(
        verbose_name="Payment Amount", max_digits=14, decimal_places=2
    )
    paymentMethod = models.CharField(
        verbose_name="Payment Method", max_length=30, choices=PAYMENT_METHOD_CHOICES
    )
    transactionReference = models.CharField(
        verbose_name="Transaction Reference", max_length=200, blank=True
    )
    notes = models.TextField(verbose_name="Notes", blank=True)
    createdBy = models.ForeignKey(
        User,
        verbose_name="Created By",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="client_payments_created",
    )
    createdDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.billing.invoiceNumber} - " f"{self.amount}"


class CompanyMembership(models.Model):
    """
    Optional membership model for users who can access more than one company.
    Existing User.company and User.role fields are retained for compatibility.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User,
        verbose_name="User",
        on_delete=models.CASCADE,
        related_name="company_memberships",
    )

    company = models.ForeignKey(
        Company,
        verbose_name="Company",
        on_delete=models.CASCADE,
        related_name="user_memberships",
    )

    role = models.ForeignKey(
        Roles,
        verbose_name="Role",
        on_delete=models.PROTECT,
        related_name="company_memberships",
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    joinedDate = models.DateTimeField(
        verbose_name="Joined Date",
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "company"],
                name="unique_user_company_membership",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.company}"
