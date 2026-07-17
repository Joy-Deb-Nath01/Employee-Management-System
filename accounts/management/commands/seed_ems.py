from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta, time
import random

from accounts.models import User
from departments.models import Department
from employees.models import Employee
from attendance.models import Attendance
from leave.models import LeaveRequest, LeaveBalance

class Command(BaseCommand):
    help = "Seed the database with default departments, role accounts, attendance logs, and leave requests for development testing."

    def handle(self, *args, **options):
        self.stdout.write("Flushing existing database records (excluding system superusers)...")
        
        # Clear existing records to ensure seed is clean and deterministic
        Attendance.objects.all().delete()
        LeaveRequest.objects.all().delete()
        LeaveBalance.objects.all().delete()
        Employee.objects.all().delete()
        Department.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        self.stdout.write("Seeding organizational departments...")
        
        dept_eng = Department.objects.create(name="Engineering", description="Software development, DevOps, and quality assurance.")
        dept_hr = Department.objects.create(name="Human Resources", description="Talent acquisition, employee relations, and policy compliance.")
        dept_mkt = Department.objects.create(name="Marketing & Growth", description="Brand management, user acquisition, and advertising campaigns.")
        dept_fin = Department.objects.create(name="Finance", description="Corporate accounting, tax filings, and budgeting.")

        self.stdout.write("Creating employee user accounts...")

        # 1. Admin/HR Accounts
        # Create standard system admin account (role: ADMIN)
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            email="admin@ems.local",
            first_name="Admin",
            last_name="System",
            role="ADMIN"
        )
        admin_user.set_password("AdminPassword123")
        admin_user.save()

        # Create HR Manager User & Employee Profile (role: HR)
        hr_user = User.objects.create(
            username="manager",
            email="manager@ems.local",
            first_name="Jane",
            last_name="Doe",
            role="HR"
        )
        hr_user.set_password("ManagerPassword123")
        hr_user.save()

        hr_employee = Employee.objects.create(
            user=hr_user,
            phone="+1 555 0100",
            date_of_birth=date(1988, 5, 14),
            gender="Female",
            address="123 Corporate Blvd, Metropolis",
            department=dept_hr,
            designation="HR Director",
            date_of_joining=date(2023, 1, 15)
        )

        # 2. Standard Employee Accounts (role: EMPLOYEE)
        # Alice (Engineering Lead)
        alice_user = User.objects.create(
            username="dev1",
            email="alice@ems.local",
            first_name="Alice",
            last_name="Smith",
            role="EMPLOYEE"
        )
        alice_user.set_password("EmployeePassword123")
        alice_user.save()

        alice_emp = Employee.objects.create(
            user=alice_user,
            phone="+1 555 0201",
            date_of_birth=date(1991, 10, 4),
            gender="Female",
            address="456 Silicon Way, Tech City",
            department=dept_eng,
            designation="Senior Engineering Lead",
            date_of_joining=date(2023, 5, 1)
        )

        # Bob (Backend Developer)
        bob_user = User.objects.create(
            username="dev2",
            email="bob@ems.local",
            first_name="Bob",
            last_name="Johnson",
            role="EMPLOYEE"
        )
        bob_user.set_password("EmployeePassword123")
        bob_user.save()

        bob_emp = Employee.objects.create(
            user=bob_user,
            phone="+1 555 0202",
            date_of_birth=date(1994, 3, 22),
            gender="Male",
            address="789 Python St, Coding Junction",
            department=dept_eng,
            designation="Backend Developer",
            date_of_joining=date(2023, 11, 10)
        )

        # Charlie (Marketing Specialist)
        charlie_user = User.objects.create(
            username="market1",
            email="charlie@ems.local",
            first_name="Charlie",
            last_name="Brown",
            role="EMPLOYEE"
        )
        charlie_user.set_password("EmployeePassword123")
        charlie_user.save()

        charlie_emp = Employee.objects.create(
            user=charlie_user,
            phone="+1 555 0301",
            date_of_birth=date(1995, 7, 18),
            gender="Other",
            address="101 Creative Ave, Brand Hills",
            department=dept_mkt,
            designation="Growth Lead",
            date_of_joining=date(2024, 2, 20)
        )

        # 3. Assign Department Heads
        dept_eng.head = alice_emp
        dept_eng.save()

        dept_hr.head = hr_employee
        dept_hr.save()

        dept_mkt.head = charlie_emp
        dept_mkt.save()

        self.stdout.write("Seeding attendance histories (last 15 business days)...")
        
        # Seed daily attendance logs (Mon-Fri) for the past 15 days
        today = date.today()
        all_employees = [hr_employee, alice_emp, bob_emp, charlie_emp]

        for i in range(15, -1, -1):
            log_date = today - timedelta(days=i)
            # Skip weekends
            if log_date.weekday() >= 5:
                continue

            for emp in all_employees:
                # For today, configure specific sandbox states
                if log_date == today:
                    if emp == alice_emp:
                        # Alice checked in at 9:02 AM but hasn't clocked out
                        Attendance.objects.create(
                            employee=emp,
                            date=log_date,
                            check_in=time(9, 2),
                            status="Present"
                        )
                    elif emp == hr_employee:
                        # HR Checked in at 9:22 AM (Late) but hasn't clocked out
                        Attendance.objects.create(
                            employee=emp,
                            date=log_date,
                            check_in=time(9, 22),
                            status="Late"
                        )
                    elif emp == charlie_emp:
                        # Charlie completed duty today
                        Attendance.objects.create(
                            employee=emp,
                            date=log_date,
                            check_in=time(8, 55),
                            check_out=time(17, 30),
                            status="Present"
                        )
                    # Bob is left un-clocked-in today to test check-in actions
                    continue

                # For past days, generate random realistic clocking entries
                roll = random.random()
                if roll < 0.05:
                    # Absent
                    Attendance.objects.create(
                        employee=emp,
                        date=log_date,
                        status="Absent"
                    )
                elif roll < 0.15:
                    # Late (between 9:16 AM and 10:30 AM)
                    c_in = time(9, random.randint(16, 59))
                    c_out = time(17, random.randint(0, 30))
                    Attendance.objects.create(
                        employee=emp,
                        date=log_date,
                        check_in=c_in,
                        check_out=c_out,
                        status="Late"
                    )
                elif roll < 0.20:
                    # Half-day (between 12:01 PM and 1:30 PM)
                    c_in = time(12, random.randint(5, 30))
                    c_out = time(17, random.randint(0, 30))
                    Attendance.objects.create(
                        employee=emp,
                        date=log_date,
                        check_in=c_in,
                        check_out=c_out,
                        status="Half-day"
                    )
                else:
                    # Standard Present (between 8:45 AM and 9:15 AM)
                    c_in = time(8, random.randint(45, 59)) if random.choice([True, False]) else time(9, random.randint(0, 15))
                    c_out = time(17, random.randint(0, 30))
                    Attendance.objects.create(
                        employee=emp,
                        date=log_date,
                        check_in=c_in,
                        check_out=c_out,
                        status="Present"
                    )

        self.stdout.write("Seeding sample leave requests...")

        # 1. Approved Leave for Alice (Sick leave, 3 days)
        req_alice = LeaveRequest.objects.create(
            employee=alice_emp,
            leave_type="Sick",
            start_date=today - timedelta(days=20),
            end_date=today - timedelta(days=18),
            reason="Suffering from severe flu. Advised bed rest by doctor.",
            status="Approved",
            remarks="Approved by HR. Get well soon."
        )
        # Deduct sick balance
        balance_alice = alice_emp.leave_balance
        balance_alice.sick_balance -= req_alice.duration
        balance_alice.save()

        # 2. Pending Casual Leave for Bob (2 days next week)
        LeaveRequest.objects.create(
            employee=bob_emp,
            leave_type="Casual",
            start_date=today + timedelta(days=4),
            end_date=today + timedelta(days=5),
            reason="Attending family function out of town.",
            status="Pending"
        )

        # 3. Rejected Earned/Annual Leave for Charlie (last week)
        LeaveRequest.objects.create(
            employee=charlie_emp,
            leave_type="Earned",
            start_date=today - timedelta(days=10),
            end_date=today - timedelta(days=6),
            reason="Plan to travel internationally for vacation.",
            status="Rejected",
            remarks="Rejected due to peak marketing campaign launch. Please reschedule after the campaign."
        )

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
        self.stdout.write(self.style.SUCCESS("---------------------------------------"))
        self.stdout.write(self.style.SUCCESS("CREDENTIALS SUMMARY FOR TESTING:"))
        self.stdout.write(self.style.SUCCESS("1. Admin Account:  username 'admin'   / password 'AdminPassword123'"))
        self.stdout.write(self.style.SUCCESS("2. HR Manager:     username 'manager' / password 'ManagerPassword123'"))
        self.stdout.write(self.style.SUCCESS("3. Developer 1:    username 'dev1'    / password 'EmployeePassword123'"))
        self.stdout.write(self.style.SUCCESS("4. Developer 2:    username 'dev2'    / password 'EmployeePassword123'"))
        self.stdout.write(self.style.SUCCESS("5. Marketer 1:     username 'market1' / password 'EmployeePassword123'"))
