# Project Report: Jenkins + Docker CI/CD Pipeline with Automated Notifications

## 1. Project Overview
This project demonstrates the implementation of a robust CI/CD pipeline using **Jenkins** and **Docker**. The pipeline is designed to automate the entire software development lifecycle, from code commit to production deployment, including automated testing and multi-channel notifications (Email/Slack).

**Objective:**
- Automate repository cloning and code linting.
- Build Docker images with unique version tagging.
- Run automated tests within the container environment.
- Deploy the application using Docker Compose.
- Configure an automated notification system for build status (Success/Failure).

---

## 2. System Architecture & Workflow
The workflow follows a standard DevOps lifecycle:
1. **Developer** pushes code to the **GitHub** repository.
2. **Jenkins** detects changes (via manual build or webhook) and triggers the pipeline defined in the `Jenkinsfile`.
3. **Pipeline Stages:**
   - **Checkout:** Pulls the latest code from the `jenkins-ci-cd-project` directory in the repository.
   - **Lint:** Performs static code analysis to ensure quality.
   - **Build:** Creates a Docker image tagged with the Jenkins Build ID.
   - **Test:** Executes Django unit tests inside the Docker container.
   - **Deploy:** Replaces the existing container with the new version using Docker Compose.
4. **Notifications:** Sends an email alert to the administrator upon success or failure.

---

## 3. Implementation Details

### 3.1 Jenkins Environment Setup
Jenkins was configured on port `8082` with the following essential plugins:
- **Docker Pipeline:** To enable native Docker commands within the script.
- **Email Extension Plugin:** For advanced email formatting and triggers.
- **Slack Notification Plugin:** For team-wide instant alerts.

### 3.2 Pipeline Configuration (Jenkinsfile)
The `Jenkinsfile` uses a declarative syntax to manage the stages. Key logic includes:
- **Environment Variables:** Defining `DOCKER_IMAGE` and `DOCKER_IMAGE_TAG`.
- **Directory Isolation:** Using the `dir()` block to target the specific project folder.
- **Self-Healing Deployment:** Added logic to remove conflicting containers (`docker rm -f`) before deployment to prevent "name in use" errors.

### 3.3 Email Notification Setup (Gmail SMTP)
To enable notifications, Jenkins was configured to use Gmail's SMTP server:
- **SMTP Server:** `smtp.gmail.com`
- **Port:** `465` (SSL)
- **Authentication:** Gmail App Password with 2FA enabled.
- **Sender Identity:** `mkcheriyan997@gmail.com`

---

## 4. Verification & Results

### 4.1 Successful Build Logs
The pipeline was successfully executed (Build #3). Console logs confirm:
- **Git Checkout:** Successful retrieval of the `jenkins-ci-cd-project` folder.
- **Docker Build:** Image `python_docker_app:3` created.
- **Test Execution:** `System check identified no issues... OK`.
- **Deployment:** Old container removed and new container started successfully.

### 4.2 Application Access
The application is live and accessible at:
[http://16.170.157.21:8000](http://16.170.157.21:8000)

---

## 5. Visual Evidence (Screenshots)

### 5.1 GitHub Repository Structure
*Evidence of the isolated project folder in the main repository.*
![GitHub Project Folder](Screenshot_GitHub_Folder.png)

### 5.2 Jenkins Pipeline Dashboard
*Overview of the pipeline stages and build history.*
![Jenkins Dashboard](Screenshot_Jenkins_Dashboard.png)

### 5.3 Pipeline Configuration
*Showing the SCM configuration pointing to the Jenkinsfile.*
![Pipeline Config](Screenshot_Pipeline_Config.png)

### 5.4 Build Success & Stage View
*Visual representation of the successful stages: Checkout, Lint, Build, Test, Deploy.*
![Stage View](Screenshot_Stage_View.png)

### 5.5 Console Output: Docker Build
*Log evidence of the Docker image creation.*
![Docker Build Log](Screenshot_Docker_Build.png)

### 5.6 Console Output: Deployment & Success
*Confirmation of the container restart and notification trigger.*
![Deployment Success](Screenshot_Deployment_Success.png)

### 5.7 Email Notification
*Proof of the success email received in the inbox.*
![Email Notification](Screenshot_Email_Proof.png)

---

## 6. Challenges & Solutions
- **Container Name Conflicts:** Initial builds failed because the container name was already taken. **Solution:** Added a `docker rm -f` command in the `Deploy` stage to ensure a clean state before every deployment.
- **SMTP Authentication:** Gmail blocked initial attempts. **Solution:** Configured a dedicated **Google App Password** and ensured the "System Admin e-mail address" matched the authenticated account.

---

## 7. Conclusion
The Jenkins CI/CD pipeline is fully operational, providing a seamless bridge between code development and production deployment. This setup ensures that every change is tested, built, and deployed automatically, with immediate feedback via email.
