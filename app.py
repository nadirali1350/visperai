from pymongo import MongoClient

from flask import Flask, render_template, request, redirect, session, sessions
import ai_program
import blog_post_gen
from myvispertools import desc, blog, emails, product, social, cv
import vispertools, ask, old_blog_post_gen


app = Flask(__name__, static_url_path='/static')
app.secret_key = 'super secret key'

client = MongoClient('mongodb+srv://nadirali1350:2Ze11yCr3qjfbdk3@visper.to6xfxz.mongodb.net/')
db = client.vispdb
users = db.users

user_schema = {
    'fullname': str,
    'pass': str,
    'email': str,
}

user_history_schema = {
    'user_email': str,
    'input_prompt': str,
    'tool_used': str,
    'generated_text': int,
    'purchase_history': str,
    'words_used': int,
    'money_saved': int,
    'time_saved': int,

}

subscription_schema = {
    'user_email': str,
    'subscription_start_date': str,
    'subscription_end_date': str,
    'current_plan': str,
    'remaining_words': str,
}

pricing_plan_schema = {
    'plan_name': str,
    'plan_price': int,
    'plan_words': int,
    'plan_duration': int,
}

discount_schema = {
    'discount_code': str,
    'discount_percentage': int,
    'discount_start_date': str,
    'discount_end_date': str,
}

billing_details_schema = {
    'user_email': str,
    'billing_address': str,
    'billing_city': str,
    'billing_state': str,
    'billing_zip': int,
    'billing_country': str,
    'billing_card_number': int,
    'billing_card_expiry': str,
    'billing_card_cvv': int,
}



# Main Route

@app.route("/" , methods=['GET', 'POST'])
def mainpage():
    

    if request.method == "POST":
        query = request.form['statment']
        open_answer = ai_program.ai_program(query)
        send_answer = open_answer
    mycheck = 0
    if mycheck == 0:
        return render_template('home/index.html', **locals())
    else:
        
        return redirect('/login')
    
    
# Register Page
@app.route("/register", methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        fullname_reg = request.form['fullname']
        email_reg = request.form['email']
        password_reg = request.form['password']
        session['email_user'] = email_reg
        session['username_login'] = fullname_reg
        print(email_reg)
        users.insert_one({
            'fullname': fullname_reg,
            'email': email_reg,
            'pass': password_reg,
            'plan_name': "FREE",
            'plan_price': 0,
            'remaining_words': 5000,
            'plan_duration': 30,
            'words_used': 0,
            'money_saved': 0,
            'time_saved': 0,})
        return redirect('/dashboard')
    return render_template("sign-up.html", **locals())


# login page
@app.route("/login", methods=['GET', 'POST'])
def login_page():
    
    if request.method == 'POST':
        email_login = request.form['email-username']
        password_login = request.form['password']
        if(users.find_one({'email': email_login, 'pass': password_login})) is None:
            
            return redirect('/')
        else:
            name_get= email_login.split('@')
            session['email_user'] = email_login
            session['username_login'] = name_get[0]
            return redirect('/dashboard')

    return render_template("sign-in.html", **locals())
   


#  Dashboard Page

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard_page():

# Getting data from database
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem_here= document['remaining_words']

    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_used= document['words_used']

    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    money_saved= document['money_saved']

    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    time_saved= document['time_saved']

# Data to Show on Dashboard
    lifetime_used_words = words_used
    total_money_saved = int(0.05 * lifetime_used_words)
    time_saved = int(lifetime_used_words / 30)
    # current_used_words= session['current_used_words']
    
    user_name = session['username_login']
    words_rem= words_rem_here
            

    return render_template("d_content.html", **locals())




#  Tool Complete Blog - blog Idea

@app.route("/blog_comp", methods=['GET', 'POST'])
def blogcomp():

    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']

    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_used= document['words_used']

    user_name = user_email
    

    if request.method == "POST":
        query = request.form['statment']
        open_answer = blog_post_gen.blog_idea(query)
        send_answer = open_answer
        session['send_answer'] = send_answer
        gene_content_len = len(send_answer.split())
        

        lifetime_used_words = lifetime_used_words + gene_content_len
        words_rem = words_rem - gene_content_len

        filter_query = {'email': user_email}
        update_query = {'$set': {'remaining_words': words_rem}}
        users.update_one(filter_query, update_query)
        
        filter_query = {'email': user_email}
        update_query = {'$set': {'words_used': lifetime_used_words}}
        users.update_one(filter_query, update_query)


        return redirect('/blog_section')


    
    
    return render_template("Tools/blog_complete/blog_idea_page.html", **locals())

#  Tool Complete Blog - blog Section

@app.route("/blog_section", methods=['GET', 'POST'])
def blogsection():
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']

    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_used= document['words_used']

    user_name = user_email

    show_idea = session['send_answer']
    return render_template("Tools/blog_complete/blog_section.html", **locals())

@app.route("/blog", methods=['GET', 'POST'])
def bloggen():
    show_idea = session['send_answer']
    if request.method == "POST":
        query = request.form['statment']
        open_answer3 = old_blog_post_gen.sections_blog(query)
        send_answer3 = open_answer3.replace('\n', '<br>')


    return render_template("Tools/one_go_blog.html", **locals())


 


# Email pages

# Confirmation Email
@app.route("/c_email", methods=['GET', 'POST'])
def confirmation_email():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']

    user_name = user_email

    if request.method == "POST":
        query = request.form['statment']
        open_answer = blog_post_gen.blog_idea(query)
        send_answer = open_answer
        session['send_answer'] = send_answer
        print(send_answer)
        print(len(send_answer))
        gene_content = len(send_answer)
        

        gene_content_len = len(send_answer.split())
        

        lifetime_used_words = lifetime_used_words + gene_content_len
        words_rem = words_rem - gene_content_len

        filter_query = {'email': user_email}
        update_query = {'$set': {'remaining_words': words_rem}}
        users.update_one(filter_query, update_query)
        
        filter_query = {'email': user_email}
        update_query = {'$set': {'words_used': lifetime_used_words}}
        users.update_one(filter_query, update_query)


        return redirect('/blog_section')

    
    
    
    return render_template("Tools/email/confirmation_email.html", **locals())

# cancelation Email
@app.route("/cn_email", methods=['GET', 'POST'])
def cancel_email():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']

    user_name = user_email

    if request.method == "POST":
        query = request.form['statment']
        open_answer = blog_post_gen.blog_idea(query)
        send_answer = open_answer
        session['send_answer'] = send_answer
        print(send_answer)
        print(len(send_answer))
        gene_content = len(send_answer)
        session['lifetime_used_words'] = session['lifetime_used_words'] - gene_content
        return redirect('/blog_section')

    
    
    
    return render_template("Tools/email/cancelation_email.html", **locals())

# Thank you Email
@app.route("/t_y_email", methods=['GET', 'POST'])
def thank_you_email():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']

    user_name = user_email

    if request.method == "POST":
        query = request.form['statment']
        open_answer = blog_post_gen.blog_idea(query)
        send_answer = open_answer
        session['send_answer'] = send_answer
        print(send_answer)
        print(len(send_answer))
        gene_content = len(send_answer)
        session['lifetime_used_words'] = session['lifetime_used_words'] - gene_content
        return redirect('/blog_section')

    
    
    
    return render_template("Tools/email/thank_you_email.html", **locals())

#Welcome email
@app.route("/w_email", methods=['GET', 'POST'])
def welcome_email():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']

    user_name = user_email

    if request.method == "POST":
        query = request.form['statment']
        open_answer = blog_post_gen.blog_idea(query)
        send_answer = open_answer
        session['send_answer'] = send_answer
        print(send_answer)
        print(len(send_answer))
        gene_content = len(send_answer)
        session['lifetime_used_words'] = session['lifetime_used_words'] - gene_content
        return redirect('/blog_section')

    
    
    
    return render_template("Tools/email/welcome_email.html", **locals())


# CV COVER LETTER
@app.route("/cover_letter", methods=['GET', 'POST'])
def cover_letter():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']

    user_name = user_email
    
    if request.method == "POST":
        company = request.form['company']
        name = request.form['name']
        position = request.form['position']

        open_answer = vispertools.write_cv_cover(company, name, position)
        send_answer = open_answer
        show_answer = open_answer.replace('\n', '<br>')
        session['send_answer'] = send_answer
        gene_content_len = len(send_answer.split())
        words_rem = words_rem - gene_content_len
        
        filter_query = {'email': user_email}
        update_query = {'$set': {'remaining_words': words_rem}}
        users.update_one(filter_query, update_query)
        

        lifetime_used_words = lifetime_used_words + gene_content_len
        filter_query = {'email': user_email}
        update_query = {'$set': {'words_used': lifetime_used_words}}
        users.update_one(filter_query, update_query)

        

    return render_template("Tools/cover_letter.html", **locals())



# Product Pros and Cons
@app.route("/product_pc", methods=['GET', 'POST'])
def product_pc():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']
    user_name = session['username_login']
    
    if request.method == "POST":
        q1 = request.form['q1']
        q2 = request.form['q2']
        open_answer = vispertools.write_product_description(q1,q2)
        send_answer = open_answer
        show_answer = open_answer.replace('\n', '<br>')
        gene_content_len = len(send_answer.split())
        words_rem = words_rem - gene_content_len
        
        filter_query = {'email': user_email}
        update_query = {'$set': {'remaining_words': words_rem}}
        users.update_one(filter_query, update_query)
        

        lifetime_used_words = lifetime_used_words + gene_content_len
        filter_query = {'email': user_email}
        update_query = {'$set': {'words_used': lifetime_used_words}}
        users.update_one(filter_query, update_query)
    
    return render_template("Tools/product/Product_PC.html", **locals())

# Product Description
@app.route("/product_desc", methods=['GET', 'POST'])
def product_description():
    
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']
    
    if request.method == "POST":
        q1 = request.form['q1']
        q2 = request.form['q2']
        open_answer = vispertools.write_product_description(q1,q2)
        send_answer = open_answer
        show_answer = open_answer.replace('\n', '<br>')
        session['send_answer'] = send_answer
        gene_content_len = len(send_answer.split())
        words_rem = words_rem - gene_content_len
        
        filter_query = {'email': user_email}
        update_query = {'$set': {'remaining_words': words_rem}}
        users.update_one(filter_query, update_query)
        

        lifetime_used_words = lifetime_used_words + gene_content_len
        filter_query = {'email': user_email}
        update_query = {'$set': {'words_used': lifetime_used_words}}
        users.update_one(filter_query, update_query)

        
        toolname= "Description writer"
        
    
    return render_template("Tools/product/product_description.html", **locals())


# Blog Description
@app.route("/blog_desc", methods=['GET', 'POST'])
def blog_description():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']
    user_name = session['username_login']
    
    if request.method == "POST":
        q1 = request.form['q1']
        q2 = request.form['q2']
        open_answer = vispertools.write_product_description(q1,q2)
        send_answer = open_answer
        show_answer = open_answer.replace('\n', '<br>')
        session['send_answer'] = send_answer
        
        

        gene_content_len = len(send_answer.split())
        words_rem = words_rem - gene_content_len
        
        filter_query = {'email': user_email}
        update_query = {'$set': {'remaining_words': words_rem}}
        users.update_one(filter_query, update_query)
        

        lifetime_used_words = lifetime_used_words + gene_content_len
        filter_query = {'email': user_email}
        update_query = {'$set': {'words_used': lifetime_used_words}}
        users.update_one(filter_query, update_query)
    
    return render_template("Tools/blog/Blog_Description.html", **locals())


# Blog FAQs
@app.route("/blog_faqs", methods=['GET', 'POST'])
def blog_faqs():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']
    user_name = session['username_login']
    
    if request.method == "POST":
        q1 = request.form['q1']
        q2 = request.form['q2']
        open_answer = vispertools.write_product_description(q1,q2)
        send_answer = open_answer
        show_answer = open_answer.replace('\n', '<br>')
        session['send_answer'] = send_answer
        

        gene_content_len = len(send_answer.split())
        words_rem = words_rem - gene_content_len
        
        filter_query = {'email': user_email}
        update_query = {'$set': {'remaining_words': words_rem}}
        users.update_one(filter_query, update_query)
        

        lifetime_used_words = lifetime_used_words + gene_content_len
        filter_query = {'email': user_email}
        update_query = {'$set': {'words_used': lifetime_used_words}}
        users.update_one(filter_query, update_query)
    
    return render_template("Tools/blog/Blog_FAQs.html", **locals())


# Blog intro
@app.route("/blog_intro", methods=['GET', 'POST'])
def blog_intro():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']
    user_name = session['username_login']
    
    if request.method == "POST":
        q1 = request.form['q1']
        q2 = request.form['q2']
        open_answer = vispertools.write_product_description(q1,q2)
        send_answer = open_answer
        show_answer = open_answer.replace('\n', '<br>')
        session['send_answer'] = send_answer
        
        gene_content_len = len(send_answer.split())
        words_rem = words_rem - gene_content_len
        
        filter_query = {'email': user_email}
        update_query = {'$set': {'remaining_words': words_rem}}
        users.update_one(filter_query, update_query)
        

        lifetime_used_words = lifetime_used_words + gene_content_len
        filter_query = {'email': user_email}
        update_query = {'$set': {'words_used': lifetime_used_words}}
        users.update_one(filter_query, update_query)
    
    return render_template("Tools/blog/Blog_Intro.html", **locals())


# Blog Idea
@app.route("/blog_idea", methods=['GET', 'POST'])
def blog_idea():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']
    user_name = session['username_login']
    
    if request.method == "POST":
        q1 = request.form['q1']
        q2 = request.form['q2']
        open_answer = vispertools.write_product_description(q1,q2)
        send_answer = open_answer
        show_answer = open_answer.replace('\n', '<br>')
        session['send_answer'] = send_answer
        

        gene_content_len = len(send_answer.split())
        words_rem = words_rem - gene_content_len
        
        filter_query = {'email': user_email}
        update_query = {'$set': {'remaining_words': words_rem}}
        users.update_one(filter_query, update_query)
        

        lifetime_used_words = lifetime_used_words + gene_content_len
        filter_query = {'email': user_email}
        update_query = {'$set': {'words_used': lifetime_used_words}}
        users.update_one(filter_query, update_query)
    
    return render_template("Tools/blog/Blog_Idea.html", **locals())


# Blog Title
@app.route("/blog_title", methods=['GET', 'POST'])
def blog_title():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']
    user_name = session['username_login']
    
    if request.method == "POST":
        q1 = request.form['q1']
        q2 = request.form['q2']
        open_answer = vispertools.write_product_description(q1,q2)
        send_answer = open_answer
        show_answer = open_answer.replace('\n', '<br>')
        session['send_answer'] = send_answer
        

        gene_content_len = len(send_answer.split())
        words_rem = words_rem - gene_content_len
        
        filter_query = {'email': user_email}
        update_query = {'$set': {'remaining_words': words_rem}}
        users.update_one(filter_query, update_query)
        

        lifetime_used_words = lifetime_used_words + gene_content_len
        filter_query = {'email': user_email}
        update_query = {'$set': {'words_used': lifetime_used_words}}
        users.update_one(filter_query, update_query)
    
    return render_template("Tools/blog/Blog_title.html", **locals())


# Digital Ad Copy
@app.route("/Digital_Ad", methods=['GET', 'POST'])
def Digital_ad():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']
    user_name = session['username_login']
    
    if request.method == "POST":
        q1 = request.form['q1']
        q2 = request.form['q2']
        open_answer = social.digital_ad(q1,q2)
        send_answer = open_answer
        show_answer = open_answer.replace('\n', '<br>')
        session['send_answer'] = send_answer
        

        gene_content_len = len(send_answer.split())
        words_rem = words_rem - gene_content_len
        
        filter_query = {'email': user_email}
        update_query = {'$set': {'remaining_words': words_rem}}
        users.update_one(filter_query, update_query)
        

        lifetime_used_words = lifetime_used_words + gene_content_len
        filter_query = {'email': user_email}
        update_query = {'$set': {'words_used': lifetime_used_words}}
        users.update_one(filter_query, update_query)
    
    return render_template("Tools/social/Digital_ad.html", **locals())



# Instagram Caption
@app.route("/Insta_caption", methods=['GET', 'POST'])
def Insta_caption():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']
    user_name = session['username_login']
    
    if request.method == "POST":
        q1 = request.form['q1']
        
        open_answer = social.instagram_caption(q1)
        send_answer = open_answer
        show_answer = open_answer.replace('\n', '<br>')
        session['send_answer'] = send_answer
        
        gene_content_len = len(send_answer.split())
        words_rem = words_rem - gene_content_len
        
        filter_query = {'email': user_email}
        update_query = {'$set': {'remaining_words': words_rem}}
        users.update_one(filter_query, update_query)
        

        lifetime_used_words = lifetime_used_words + gene_content_len
        filter_query = {'email': user_email}
        update_query = {'$set': {'words_used': lifetime_used_words}}
        users.update_one(filter_query, update_query)


    return render_template("Tools/social/Instagram_Caption.html", **locals())



# Funny Quotes
@app.route("/funny_quotes", methods=['GET', 'POST'])
def funny_q():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']
    user_name = session['username_login']
    
    if request.method == "POST":
        q1 = request.form['q1']
        
        open_answer = social.funny_q(q1)
        send_answer = open_answer
        show_answer = open_answer.replace('\n', '<br>')
        session['send_answer'] = send_answer
        

        gene_content_len = len(send_answer.split())
        words_rem = words_rem - gene_content_len
        
        filter_query = {'email': user_email}
        update_query = {'$set': {'remaining_words': words_rem}}
        users.update_one(filter_query, update_query)
        

        lifetime_used_words = lifetime_used_words + gene_content_len
        filter_query = {'email': user_email}
        update_query = {'$set': {'words_used': lifetime_used_words}}
        users.update_one(filter_query, update_query)
    
    return render_template("Tools/social/Funny_Quotes.html", **locals())



# Hashtags
@app.route("/hashtag", methods=['GET', 'POST'])
def hashtag():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']
    user_name = session['username_login']
    
    if request.method == "POST":
        q1 = request.form['q1']
        
        open_answer = social.hash_tag(q1)
        send_answer = open_answer
        show_answer = open_answer.replace('\n', '<br>')
        session['send_answer'] = send_answer
        

        gene_content_len = len(send_answer.split())
        words_rem = words_rem - gene_content_len
        
        filter_query = {'email': user_email}
        update_query = {'$set': {'remaining_words': words_rem}}
        users.update_one(filter_query, update_query)
        

        lifetime_used_words = lifetime_used_words + gene_content_len
        filter_query = {'email': user_email}
        update_query = {'$set': {'words_used': lifetime_used_words}}
        users.update_one(filter_query, update_query)
    
    return render_template("Tools/social/Hashtag.html", **locals())



# Meme writer
@app.route("/meme_write", methods=['GET', 'POST'])
def meme_write():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']
    user_name = session['username_login']
    
    if request.method == "POST":
        q1 = request.form['q1']
        
        open_answer = social.Memes_idea(q1)
        send_answer = open_answer
        show_answer = open_answer.replace('\n', '<br>')
        session['send_answer'] = send_answer
        

        gene_content_len = len(send_answer.split())
        words_rem = words_rem - gene_content_len
        
        filter_query = {'email': user_email}
        update_query = {'$set': {'remaining_words': words_rem}}
        users.update_one(filter_query, update_query)
        

        lifetime_used_words = lifetime_used_words + gene_content_len
        filter_query = {'email': user_email}
        update_query = {'$set': {'words_used': lifetime_used_words}}
        users.update_one(filter_query, update_query)
    
    return render_template("Tools/social/Memes.html", **locals())



# Youtube IDEA
@app.route("/Youtube_idea", methods=['GET', 'POST'])
def Youtube_idea():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']
    user_name = session['username_login']
    
    if request.method == "POST":
        q1 = request.form['q1']
        q2 = request.form['q2']
        open_answer = vispertools.write_product_description(q1,q2)
        send_answer = open_answer
        show_answer = open_answer.replace('\n', '<br>')
        session['send_answer'] = send_answer
        

        gene_content_len = len(send_answer.split())
        words_rem = words_rem - gene_content_len
        
        filter_query = {'email': user_email}
        update_query = {'$set': {'remaining_words': words_rem}}
        users.update_one(filter_query, update_query)
        

        lifetime_used_words = lifetime_used_words + gene_content_len
        filter_query = {'email': user_email}
        update_query = {'$set': {'words_used': lifetime_used_words}}
        users.update_one(filter_query, update_query)
    
    return render_template("Tools/social/Youtube_idea.html", **locals())


#ASK you
@app.route("/askme", methods=['GET', 'POST'])
def ask_you():
    
    user_email=session['email_user']
    document = users.find_one({"email": user_email})
    words_rem= document['remaining_words']
    lifetime_used_words= document['words_used']
    user_name = session['username_login']
    
    if request.method == "POST":
        q1 = request.form['q1']
        
        open_answer = ask.ask_here(q1)
        send_answer = open_answer
        show_answer = open_answer.replace('\n', '<br>')
        session['send_answer'] = send_answer
        

        gene_content_len = len(send_answer.split())
        words_rem = words_rem - gene_content_len
        
        filter_query = {'email': user_email}
        update_query = {'$set': {'remaining_words': words_rem}}
        users.update_one(filter_query, update_query)
        

        lifetime_used_words = lifetime_used_words + gene_content_len
        filter_query = {'email': user_email}
        update_query = {'$set': {'words_used': lifetime_used_words}}
        users.update_one(filter_query, update_query)
        
    return render_template("Tools/ask.html", **locals())

if __name__ == "__main__":
    app.run(debug=True)


