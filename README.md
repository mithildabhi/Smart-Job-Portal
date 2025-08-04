# Smart Job Portal

Welcome to the **Smart Job Portal** project! This is a web application designed and built by Meet (meet5324), Mithil (mithildabhi), Harsh (ghadiyaharsh) from scratch. My goal was to make job searching and hiring easy for both students and companies using Python, Django, and modern web technologies.

---

## 🌟 What Is This For?

This is a job portal where:
- **Companies** can create accounts, post jobs, manage hiring, and edit their company profile (logo, info, and more) with a smooth, user-friendly interface.
- **Students** can register, create a professional profile, upload resumes and projects, apply for jobs, and edit every section of their profile—almost everything is editable in a modal with live update!

Everything is built and styled by hand—no code generators or AI stubs. What you see is the result of real learning, experiments, and coding.

---

## 📁 Project Structure

The folder layout is meant to be simple:
```
companies/      # Company registration, dashboard, profile, job posting
students/       # Student registration, profile, skills, applications
jobs/           # Job listing, job applications, management
templates/      # HTML for all screens; includes modals and base templates
static/         # CSS, JavaScript (includes custom modal & profile styles)
jobportal/      # Django project settings
.gitignore      # Ignore for version control
manage.py       # Django's main management file
requirements.txt# All dependencies you need to install
render.yaml     # (optional) Settings for Render cloud deployment
setup_guide.txt # Step-by-step setup (repeat here for your ease)
```

---

## 🚀 Getting Started (For Beginners)

**If you have zero experience, just follow each step:**

1. **Install Python (if not already installed).**  
   - Download Python at [python.org](https://python.org) and install (any 3.10+ is fine).

2. **Download this project**  
   - Click the green "Code" button above, then "Download ZIP", or `git clone` this repo if you have Git.

3. **Open a terminal/command prompt.**  
   - Navigate to the folder you downloaded:  
   `cd path/to/jobportal`

4. **Create and activate a virtual environment (recommended):**
    ```
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On Mac/Linux:
    source venv/bin/activate
    ```

5. **Install required packages:**
    ```
    pip install -r requirements.txt
    ```

6. **Run database migrations:**
    ```
    python manage.py migrate
    ```

7. **(Optional) Create a superuser (admin):**
    ```
    python manage.py createsuperuser
    ```

8. **Start the development server:**
    ```
    python manage.py runserver
    ```

9. **Open your browser at:**  
    `http://127.0.0.1:8000/`

---

## 🧭 What You Can Do In The App

- **Students:**
  - Register for a new account.
  - Log in and build your profile with skills, education, experience, and projects.
  - Upload and change your profile picture.
  - Any section ("Edit Information", "Add Skills", "Add Experience", "Add Project") can be edited instantly using modern modal dialogs with AJAX for a live, no-page-reload experience!
  - Browse and apply to jobs; track your applications.

- **Companies:**
  - Register as a company and update your company logo, info, and description all in-place.
  - Post jobs, view applicant stats, edit job info right on the dashboard.
  - All company profile fields are editable live with modals, matching the student experience.

- **Admins:**  
  - Can manage everything using Django's admin panel at `/admin`.

---

## 👩‍💻 How Is It Built?

- **Python 3.10+**
- **Django** web framework
- **Bootstrap 5** for styling and responsive layouts
- **Custom CSS** for personalized appearance (see `static/` directory)
- **AJAX with Fetch API** for live editing modals (see company/student profile editing)
- **Django ORM** for the database (no SQL needed for beginners)
- **Modular code**: Each app (companies, students, jobs) has its own logic and templates.

---

## 💡 What Makes This Unique?

- Hand-written logic, views, templates, and styles.  
- AJAX-powered modals for editing (no full page reloads when you edit info!).
- Designed for clarity: If you’re learning Django, the code and comments will actually help you.
- The UI "feels" modern, yet you can trace every file back to a human developer (me).

---

## ✍️ Personal Words

This project was made line-by-line while learning Django, Bootstrap, and best practices in user experience.  
If you are new to web dev, check out the code in `students/`, `companies/`, and `jobs/`—you’ll find well-commented views, and you can run this with almost zero setup.  
If you have suggestions, issues, or just want to say hi, please do! This project is as much for learning as it is for helping others.

---

## 📝 Troubleshooting & FAQ

**I get an error about migrations:**  
Run `python manage.py migrate` first.

**How do I create a user?**  
Start the server and register at `/students/register/` (for students) or `/companies/register/`.

**Where do I change code for modals/AJAX?**  
Look in `students/templates/students/profile.html` or the equivalent in `companies/`.

**Want to deploy on Render or another cloud?**  
See `render.yaml` and use the guide in `setup_guide.txt`.

---

## 🏁 Thanks!

Thanks for checking out the project and reading this README!  
If you actually run it, message me what works and what breaks.  
Every directory and commit here is written by a human, not an auto-generator.  
Happy coding!



