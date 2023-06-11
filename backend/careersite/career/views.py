from django.shortcuts import render
from django.db import connection, connections
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views import View
from datetime import date
from datetime import datetime, timedelta
from django.shortcuts import redirect
from django.contrib import messages
from django.middleware.csrf import get_token

class HomeView(View):
    def get(self, request):
        if 'username' in request.session:
            user_id = request.session['user_id']
            user_type = request.session['user_type']
            username = request.session['username']

            # reports
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM job_application_count WHERE application_count = "
                           "(SELECT MAX(application_count) FROM job_application_count)")
            most_popular_job = cursor.fetchone()

            cursor.execute("SELECT average_age FROM average_age_view")
            average_age = cursor.fetchone()

            context = {'user_type': user_type, 'username': username, 'user_id': user_id,
                       'most_popular_job': most_popular_job, 'average_age': average_age}
        
            return render(request, 'career/home.html', context)
        return HttpResponseRedirect("/login")

class UsersView(View):
    def get(self, request):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM User;")
        users = cursor.fetchall()
        cursor.close()

        return render(request, 'career/users.html', {'users': users})


class LoginView(View):
    def get(self, request):
        return render(request, 'career/login.html')

    def post(self, request):
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        try:
            statement = "SELECT * FROM User Where username= '" + username + "' AND password='" + password + "'"
            cursor = connection.cursor()
            cursor.execute(statement)
            user = cursor.fetchone()
            cursor.close()

        except:
            print("db cannot be found")
            
            return render(request, 'career/login.html')

        if user != None:
                request.session['username'] = username
                request.session['user_id'] = user[0]
                request.session['user_type'] = user[7]
                print("--------------------", request.session['user_type'])
                success = True
                context = {'success': success, 'username': username}
                messages.success(request, 'You logged the system successfully')
                
                return HttpResponseRedirect("/home")
        else:
            messages.error(request, 'User cannot be found')
            
            return render(request, 'career/login.html')


class SignUpView(View):
    def get(self, request):
        return render(request, 'career/signup.html')

    def post(self, request):
        username = request.POST.get("username", "")
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        passwordver = request.POST.get("passwordverification", "")
        fullname = request.POST.get("fullname", "")
        user_type = request.POST.get("usertype", "")
        registration_time = datetime.now() + timedelta(hours=3)

        if password != passwordver:
            print("passwords are not same")
            
            return render(request, 'career/signup.html')
        else:
            if username !="" and email != "" and password != "":
                parameters = [fullname, username, password, email, registration_time, user_type]
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO User(full_name, username, password, email_address, date_of_registration, user_type) VALUES(%s,%s,%s,%s,%s, %s);",
                    parameters)
                cursor.close()
                connection.commit()

                cursor = connection.cursor()
                cursor.execute("SELECT user_id FROM USER WHERE username = '" + username + "'")
                user_id = cursor.fetchone()
                cursor.close()

                cursor = connection.cursor()
                cursor.execute("INSERT INTO NonAdmin(user_id) VALUES(%s);", user_id)
                cursor.close()
                connection.commit()
                print(user_type)

                if user_type == "Job Hunter":
                    cursor = connection.cursor()
                    cursor.execute("INSERT INTO RegularUser(user_id) VALUES(%s);", user_id)
                    cursor.close()
                    connection.commit()

                elif user_type == "Recruiter":
                    cursor = connection.cursor()
                    cursor.execute("INSERT INTO Recruiter(user_id) VALUES(%s);", user_id)
                    cursor.close()
                    connection.commit()

                elif user_type == "Career Expert":
                    cursor = connection.cursor()
                    cursor.execute("INSERT INTO CareerExpert(user_id) VALUES(%s);", user_id)
                    cursor.close()
                    connection.commit()

                print("user is successfully created")
                
                return HttpResponseRedirect("/login")
            else:
                print("Please fill all information")
                
                return render(request, 'career/signup.html')

class LogoutView(View):
    def get(self, request):
        request.session.flush()
        
        return HttpResponseRedirect("/")

class JobListingsView(View):
    def get( self, request ):
        user_id = request.session['user_id']
        
        search_term = request.GET.get('term', '')
        cursor = connection.cursor()
        query = "SELECT * FROM Company AS C JOIN Job AS J ON C.company_id = J.company_id"

        if search_term is not None:
            query += " WHERE J.title LIKE %s OR  C.name LIKE %s OR J.profession LIKE %s"
            cursor.execute(query, [('%' + search_term + '%'), ('%' + search_term + '%'), ('%' + search_term + '%')])
        else:
            cursor.execute(query)
        jobs = cursor.fetchall()
        cursor.close()
        
        cursor = connection.cursor()
        cursor.execute("SELECT job_id FROM Application WHERE user_id = %s;", [request.session['user_id']])
        applied_jobs = cursor.fetchall()
        cursor.close()
        
        applied_job_ids = []
        
        for applied_job in applied_jobs:
            applied_job_ids.append(applied_job[0])

        return render(request, 'career/joblist.html', {
            'jobs': jobs,
            'user_id': user_id,
            'user_type': request.session['user_type'],
            'applied_job_ids': applied_job_ids,
        });

class JobDescriptionView(View):
    def get(self, request, job_id):
        cursor = connection.cursor() 
        cursor.execute("SELECT * FROM Job j JOIN Company c ON j.company_id = c.company_id WHERE job_id = %s;", [job_id])
        job = cursor.fetchone()
        cursor.close()
        
        user_type = request.session['user_type']
        
        return render(request, 'career/job-detail.html', {'job': job, 'user_type': user_type})

    def post(self, request, job_id):
        user_id = request.session['user_id']
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Job WHERE job_id=%s", [job_id])
        job = cursor.fetchone()
        cursor.close()

        personal_informaion = request.POST.get("personal-information", "")
        date = datetime.now() + timedelta(hours=3)

        cursor = connection.cursor()
        cursor.execute("INSERT INTO Application(user_id, job_id, date, personal_info, cv_url) VALUES(%s, %s, %s, %s, %s);",
                       (user_id, job_id, date, personal_informaion, ""))
        connection.commit()
        cursor.close()

        return redirect("job-list")

class PastApplicationsView(View):
    def get(self, request):
        user_id = request.session['user_id']
        cursor = connection.cursor()
        cursor.execute("SELECT J.title, C.name, A.date, J.profession, J.location, J.job_requirements FROM Application as A JOIN Job as J JOIN Company as C WHERE A.job_id=J.job_id AND J.company_id = C.company_id AND A.user_id=%s ORDER BY A.date DESC", [user_id])
        pastJobs = cursor.fetchall()
        cursor.close()

        return render(request, 'career/application-list.html', {'pastJobs': pastJobs})
    
class PastOpeningsView(View):
    def get(self, request):
        user_id = request.session['user_id']
        cursor = connection.cursor()
        cursor.execute("SELECT J.title, C.name, J.due_date, J.profession, J.location, J.job_requirements FROM Job as J JOIN Company as C WHERE J.company_id = C.company_id AND J.recruiter_id=%s ORDER BY J.due_date DESC", [user_id])
        pastOp = cursor.fetchall()
        cursor.close()

        return render(request, 'career/past-openings.html', {'pastOp': pastOp, 'user_type': request.session['user_type']})

class AddJobView(View):
    def get(self, request):
        user_id = request.session['user_id']
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM User NATURAL JOIN Recruiter WHERE user_id = %s;", [user_id])
        recruiter = cursor.fetchone()
        cursor.close()
        
        cursor = connection.cursor()
        cursor.execute("SELECT company_id FROM NonAdmin WHERE user_id = %s;", [user_id])
        company_id = cursor.fetchone()
        cursor.close()
        
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Company WHERE company_id = %s;", company_id)
        company = cursor.fetchone()
        cursor.close()

        if recruiter is None:
            return redirect('job-list')
        else:
            return render(request, 'career/add_job.html', {'company': company})

    def post(self, request):
        user_id = request.session['user_id']
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM NonAdmin NATURAL JOIN Recruiter WHERE user_id = %s;", [user_id])
        recruiter = cursor.fetchone()
        cursor.close()
        
        if recruiter is None:
            return redirect('job-list')
        else:
            title = request.POST.get("job-title", "")
            due_date = request.POST.get("due-date", "")
            profession = request.POST.get("job-profession", "")
            location = request.POST.get("job-location", "")
            job_requirements = request.POST.get("job-requirements", "")
            description = request.POST.get("job-description", "")

            if title != "":
                cursor = connection.cursor()
                cursor.execute("INSERT INTO Job(company_id, recruiter_id, title, due_date, profession, location, "
                               "job_requirements, description) VALUES(%s, %s, %s, %s, %s, %s, %s, %s);",
                               (recruiter[1], recruiter[0], title, due_date, profession, location, job_requirements,
                                description))
                connection.commit()
                cursor.close()
                messages.success(request, "Message is added")

                return redirect('job-list')
            else:
                return render(request, 'career/add-job.html')

class EditJobView(View):
    def get(self, request, job_id):
        user_id = request.session['user_id']
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM User NATURAL JOIN Recruiter WHERE user_id = %s;", [user_id])
        recruiter = cursor.fetchone()
        cursor.close()
        
        cursor = connection.cursor()
        cursor.execute("SELECT company_id FROM NonAdmin WHERE user_id = %s;", [user_id])
        company_id = cursor.fetchone()
        cursor.close()
        
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Company WHERE company_id = %s;", company_id)
        company = cursor.fetchone()
        cursor.close()
        
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Job WHERE job_id = %s;", [job_id])
        job = cursor.fetchone()
        cursor.close()
        
        if recruiter is None:
            return redirect('job-list')
        else:
            return render(request, 'career/edit_job.html', {'company': company, 'job': job})

    def post(self, request, job_id):
        user_id = request.session['user_id']
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM NonAdmin NATURAL JOIN Recruiter WHERE user_id = %s;", [user_id])
        recruiter = cursor.fetchone()
        cursor.close()
        
        if recruiter is None:
            return redirect('job-list')
        else:
            title = request.POST.get("job-title", "")
            due_date = request.POST.get("due-date", "")
            profession = request.POST.get("job-profession", "")
            location = request.POST.get("job-location", "")
            job_requirements = request.POST.get("job-requirements", "")
            description = request.POST.get("job-description", "")

            if title != "":
                cursor = connection.cursor()
                cursor.execute("UPDATE Job SET title=%s, due_date=%s, profession=%s, location=%s, job_requirements=%s, description=%s WHERE job_id=%s;", (title, due_date, profession, location, job_requirements, description, job_id))
                connection.commit()
                cursor.close()
                messages.success(request, "Message is added")

                return redirect('job-list')
            else:
                return render(request, 'career/edit-job.html')

class CandidatesView(View):
    def get(self, request, job_id):
        user_id = request.session['user_id']
        cursor = connection.cursor()
        cursor.execute("SELECT U.full_name, U.email_address, A.cv_url, U.dp_url, A.personal_info, A.date FROM Job as J JOIN Application as A JOIN User as U WHERE U.user_id=A.user_id AND J.job_id=A.job_id AND J.job_id=%s AND J.recruiter_id=%s ORDER BY A.date ASC", [job_id, user_id])
        candidates = cursor.fetchall()
        cursor.close()

        return render(request, 'career/candidates.html', {'candidates': candidates})

class PostListView(View):
    def get(self, request):

        ordering = request.GET.get('ordering', '')  # Default ordering if not provided

        user_id = request.session['user_id']

        query = "SELECT *, count(P.post_id) as num_of_comments FROM Post as P NATURAL JOIN User " \
                "LEFT JOIN Comment as C ON P.post_id = C.post_id " \
                "WHERE 1=1 GROUP BY P.post_id"

        params = []

        if ordering == 'oldest':
            query += " ORDER BY date"
        elif ordering == "newest":
            query += " ORDER BY date DESC"
        elif ordering == "most_popular":
            query += " ORDER BY num_of_comments DESC"

        cursor = connection.cursor()
        cursor.execute(query, params)
        posts = cursor.fetchall()
        cursor.close()

        return render(request, 'career/post_list.html', {'posts': posts, 'user_id': user_id})

class AddPostView(View):
    def get(self, request):
        return render(request, 'career/add_post.html')

    def post(self, request):
        user_id = request.session['user_id']
        content = request.POST.get("content", "")
        title = request.POST.get("title","")
        if content != "":
            date = datetime.now() + timedelta(hours=3)
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Post(user_id, title, content, date) VALUES(%s, %s, %s, %s);",
                           (user_id, title, content, date));
            connection.commit()
            cursor.close()
            messages.success(request, "Message is added")
        
            return redirect('/post-list')
        
        return render(request, 'career/add_post.html')
    
class DeletePostView(View):
    def get(self, request, post_id):
        print('deneme')
        user_id = request.session['user_id']
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM Post WHERE post_id = %s;", [post_id])
        post_user_id = cursor.fetchone()
        cursor.close()

        csrf_token = get_token(request)
        headers = {'X-CSRFToken': csrf_token}
        
        if post_user_id[0] != user_id:
            messages.error(request, "You are not permitted to delete this post")
        else:
            cursor = connection.cursor()
            print('deneme')
            cursor.execute('DELETE FROM Comment WHERE post_id = %s', (post_id,))
            cursor.execute('DELETE FROM Post WHERE post_id = %s', (post_id,))
            connection.commit()
            cursor.close()

        return redirect("/post-list", headers=headers)

class PostDetailView(View):
    def get(self, request, post_id):
        user_id = request.session['user_id']
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Post NATURAL JOIN User WHERE post_id = %s;", [post_id])
        post = cursor.fetchone()
        cursor.close()

        # get all comments which belong to the chosen post
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Comment NATURAL JOIN User WHERE post_id = %s", [post_id])
        comments = cursor.fetchall()
        cursor.close()

        context = {'user_id': user_id, 'post':post, 'comments': comments}
        return render(request, 'career/post_detail.html', context)

    # for comment section
    def post(self, request, post_id):
        user_id = request.session['user_id']
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM Post WHERE post_id =%s", [post_id])
        post = cursor.fetchone()
        cursor.close()

        # get all comments which belong to the chosen post
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Comment WHERE post_id =%s ", [post_id])
        comments = cursor.fetchall()
        cursor.close()

        content = request.POST.get("content", "")
        date = datetime.now() + timedelta(hours=3)

        cursor = connection.cursor()
        cursor.execute("INSERT INTO Comment(user_id, post_id, CONTENT, date) VALUES(%s, %s, %s, %s);",
                       (user_id, post_id, content, date))
        connection.commit()
        cursor.close()

        context = {'user_id': user_id, 'post': post, 'comments': comments}
        
        return redirect("post-detail", post_id=post_id)


class DeleteCommentView(View):
    def get(self, request, comment_id):
        user_id = request.session['user_id']
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, post_id FROM Comment WHERE comment_id = %s", [comment_id])
        result = cursor.fetchone()
        if result is None:
            messages.error(request, 'comment-cannot-be-found')
            return redirect('post-list')

        comment_user_id = result[0]
        post_id = result[1]
        cursor.close()
        if comment_user_id != user_id:
            messages.error(request, "You are not permitted to delete this post")
        else:
            cursor = connection.cursor()
            cursor.execute('DELETE FROM Comment WHERE comment_id = %s', [comment_id])
            connection.commit()
            cursor.close()

        return redirect('post-detail', post_id=post_id)

class DeleteJobView(View):
    def get(self, request, job_id):
        user_id = request.session['user_id']
        cursor = connection.cursor()
        cursor.execute("SELECT recruiter_id, company_id FROM Job WHERE job_id = %s", [job_id])
        result = cursor.fetchone()
        if result is None:
            messages.error(request, 'comment-cannot-be-found')
            return redirect('job-list')

        job_recruiter_id = result[0]
        job_company_id = result[1]
        cursor.close()
        
        if job_recruiter_id != user_id:
            messages.error(request, "You are not permitted to delete this post")
        else:
            cursor = connection.cursor()
            cursor.execute('DELETE FROM Application WHERE job_id = %s', [job_id])
            connection.commit()
            cursor.close()
            
            cursor = connection.cursor()
            cursor.execute('DELETE FROM Job WHERE job_id = %s', [job_id])
            connection.commit()
            cursor.close()

        return redirect('job-list')

class AddExperience(View):
    def get(self, request):
        user_id = request.session['user_id']
        cursor = connection.cursor()
        
        return render(request, 'career/add_experience.html')

# PROFILE VIEW #
class ProfileView(View):
    def get(self, request, profile_id):
        current_user_id = request.session['user_id']
        
        cursor = connection.cursor()
        cursor.execute("SELECT user_type FROM User WHERE user_id=%s", [profile_id])
        profile_user_type = cursor.fetchone()
        cursor.close()

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM User WHERE user_id=%s", [profile_id])
        user = cursor.fetchone()
        cursor.close()

        cursor = connection.cursor()
        cursor.execute("SELECT user_type FROM User WHERE user_id=%s", [current_user_id])
        current_user_type = cursor.fetchone()
        cursor.close()
        
        cursor = connection.cursor()
        if profile_user_type[0] == 'RegularUser':
            cursor.execute("SELECT U.full_name, N.birth_date, U.email_address, U.dp_url, U.username, U.password, N.profession, C.name, N.skills, R.portfolio_url, R.avg_career_grd FROM RegularUser as R JOIN NonAdmin as N JOIN User as U JOIN Company as C WHERE N.company_id = C.company_id AND R.user_id = N.user_id AND N.user_id = U.user_id AND U.user_id=%s", [profile_id])
        elif profile_user_type[0] == 'Recruiter':
            cursor.execute("SELECT U.full_name, N.birth_date, U.email_address, U.dp_url, U.username, U.password, N.profession, C.name, N.skills FROM Recruiter as R JOIN NonAdmin as N JOIN User as U JOIN Company as C WHERE N.company_id = C.company_id AND R.user_id = N.user_id AND N.user_id = U.user_id AND U.user_id=%s", [profile_id])
        elif profile_user_type[0] == 'CareerExpert':
            cursor.execute("SELECT U.full_name, N.birth_date, U.email_address, U.dp_url, U.username, U.password, N.profession, CO.name, N.skills FROM CareerExpert as C JOIN NonAdmin as N JOIN User as U JOIN Company as CO WHERE CO.company_id = N.company_id AND C.user_id = N.user_id AND N.user_id = U.user_id AND U.user_id=%s", [profile_id])
        elif profile_user_type[0] == 'Admin':
            return render(request, 'career/user.html', {'user': user, 'user_info': None, 'current_user_type': current_user_type[0], 'profile_user_type': profile_user_type[0], 'current_user_id': current_user_id})
        user_info = cursor.fetchall()
        cursor.close()
        
        return render(request, 'career/user.html', {'user': user, 'user_info': user_info[0], 'current_user_type': current_user_type[0], 'profile_user_type': profile_user_type[0], 'current_user_id': current_user_id})

class ProfileEditView(View):
    def get(self, request, user_id):
        real_user_id = request.session['user_id']
        
        if real_user_id != user_id:
            return redirect('user', profile_id = user_id)
        
        cursor = connection.cursor()
        cursor.execute("SELECT user_type FROM User WHERE user_id = %s;", [user_id])
        user_type = cursor.fetchone()
        cursor.close()
        
        cursor = connection.cursor()
        if user_type[0] == 'RegularUser':
            cursor.execute("SELECT * FROM User NATURAL JOIN NonAdmin NATURAL JOIN RegularUser WHERE user_id = %s;", [user_id])
        elif user_type[0] == 'Recruiter':
            cursor.execute("SELECT * FROM User NATURAL JOIN NonAdmin WHERE user_id = %s;", [user_id])
        elif user_type[0] == 'CareerExpert':
            cursor.execute("SELECT * FROM User NATURAL JOIN NonAdmin WHERE user_id = %s;", [user_id])
        else:
            cursor.execute("SELECT * FROM User WHERE user_id = %s;", [user_id])
        user = cursor.fetchone()
        cursor.close()

        return render(request, 'career/edit_profile.html', {'user_type': user_type, 'user': user})

    def post(self, request, user_id):
        real_user_id = request.session['user_id']
        
        if real_user_id != user_id:
            return redirect('user', profile_id = user_id)
        
        cursor = connection.cursor()
        cursor.execute("SELECT user_type FROM User WHERE user_id = %s;", [user_id])
        user_type = cursor.fetchone()
        cursor.close()
        
        full_name = request.POST.get("full-name", "")
        email_address = request.POST.get("email-address", "")
        birth_date  = request.POST.get("birth-date", "")
        profession = request.POST.get("profession", "")
        skills = request.POST.get("skills", "")
        portfolio_url = request.POST.get("portfolio-url", "")

        if full_name != "" and email_address != "":
            cursor = connection.cursor()
            cursor.execute("UPDATE User SET full_name=%s, email_address=%s WHERE user_id=%s;", (full_name, email_address, user_id))
            
            if user_type[0] != 'Admin':
                cursor.execute("UPDATE NonAdmin SET birth_date=%s, profession=%s, skills=%s WHERE user_id=%s;", (birth_date, profession, skills, user_id))
            if user_type[0] == 'RegularUser':   
                cursor.execute("UPDATE RegularUser SET portfolio_url=%s WHERE user_id=%s;", (portfolio_url, user_id))
            
            connection.commit()
            cursor.close()
            
        return redirect('user', profile_id=real_user_id)

class GradingView(View):
    def get(self, request, user_id):
        expert_id = request.session['user_id']
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM CareerExpert WHERE user_id=%s", [expert_id])
        expert = cursor.fetchone()

        cursor.execute("SELECT * FROM RegularUser Natural Join User WHERE user_id=%s", [user_id])
        user = cursor.fetchone()

        if expert is None:
            return redirect('user', user_id=user_id)
        else:
            context = {'user': user, 'user_id': user_id}
            
            return render(request, 'career/grading.html', context)

    def post(self, request, user_id):
        expert_id = request.session['user_id']
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM CareerExpert WHERE user_id=%s", [expert_id])
        expert = cursor.fetchone()

        cursor.execute("SELECT * FROM RegularUser Natural Join User WHERE user_id=%s", [user_id])
        user = cursor.fetchone()
        cursor.close()

        if expert is None or user is None:
            return redirect('user', user_id=user_id)
        else:
            grade = request.POST.get("grade", 5)
            feedback = request.POST.get("feedback", "")

            parameters = [user_id, expert_id, grade, feedback]
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO CareerGrade(user_id, expert_id, grade, feedback_text ) VALUES(%s,%s,%s,%s);",
                parameters)

            cursor.close()
            connection.commit()

            return redirect('home')
