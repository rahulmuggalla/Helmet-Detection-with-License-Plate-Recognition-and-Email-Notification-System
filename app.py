from flask import Flask, flash, render_template, url_for, session, redirect, request
from flask_session import Session
import mysql.connector
import os
import smtplib

from save_bike import save_bike
from no_helmet_save import save_no_helmet
from mail_db_loop import recognize_plate, send_email

from no_helmet_img import save_no_helmet_img


app = Flask(__name__)

# Check Configuration section for more details

app.config['SESSION_TYPE']='filesystem'
app.config['SECRET_KEY']='super_secret_key'

mydb = mysql.connector.connect(host='localhost', user='root', password='admin', db='helmet_project')

Session(app)

@app.route('/',methods=['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('home'))
    if request.method=='POST':
        id=request.form['id']
        password=request.form['password']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*) from user where id=%s and password=%s',[id,password])
        count=cursor.fetchone()[0]
        if count==0:
            flash('Invalid Id or Password')
            return render_template('login.html')
        else:
            session['user']=id
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('user'):
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
            
        cursor = mydb.cursor(buffered=True)
        cursor.execute('INSERT INTO user (id, email, password) VALUES (%s, %s, %s)', [username, email, password])
        mydb.commit()
            
        session['user'] = username
        return redirect(url_for('home'))
    
    return render_template('sign_up.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if session.get('user'):
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form['email']
        
        # Perform the necessary database operations to check if the email exists in the table
        # Example code for checking email in the user table
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT id, password FROM user WHERE email = %s', [email])
        pswd = cursor.fetchone()
        
        if pswd is None:
            flash('Email not found.')
            return render_template('forgot_password.html')
        
        # If the email exists, send an email to the user with their user ID
        # Replace the placeholders with your email configuration details
        sender_email = "rahulmuggalla02@gmail.com"
        sender_password = "gxnlvbfnssorjgkt"
        subject = "Forgot Details ?"
        message = f'''Your User ID is : {pswd[0]} 
Your Password is : {pswd[1]}'''
        
        try:
            # Establish a secure connection with the SMTP server
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            # Log in to the email account
            server.login(sender_email, sender_password)
            # Send the email
            server.sendmail(sender_email, email, f"Subject: {subject}\n\n{message}")
            # Close the connection
            server.quit()
            
            flash('An email with your Password has been sent to your registered email address.')
            return redirect(url_for('login'))
        except Exception as e:
            # Handle any errors that occur during the email sending process
            flash('An error occurred while sending the email.')
            print(e)
            return render_template('forgot_password.html')
    
    return render_template('forgot_password.html')


@app.route('/home', methods=['GET','POST'])
def home():
    if session.get('user'):
        return render_template('home.html')
    else:
        return redirect(url_for('login'))

@app.route('/upload_vid', methods=['GET','POST'])
def upload_vid():
    if session.get('user'):
        cursor = mydb.cursor()
        cursor.execute('select * from info2 where added_by = %s', (session.get('user'),))
        data1 = cursor.fetchall()
        if request.method=='POST':
            path=os.path.dirname(os.path.abspath(__file__))
            video=request.files['upload_vid']
            video.save(os.path.join(path,'static/video/',video.filename))
            save_bike(os.path.join(path,'static/video/',video.filename))
            save_no_helmet(os.path.join(path,'static/Person_Bike'+video.filename))
            data_pth= os.path.join(path,'static/No_Helmet')
            filedata=os.listdir(data_pth)
            dict_data=[(i,recognize_plate(os.path.join(data_pth,i)),session.get('user')) for i in filedata]
            #print(dict_data)
            cursor = mydb.cursor()
            cursor.executemany('insert into info2 values(%s, %s, %s)', dict_data)
            mydb.commit()
            cursor.execute('select * from info2 where added_by = %s', (session.get('user'),))
            data1 = cursor.fetchall()
            if data1[0]!=('None',):
                #data=tuple(dict_data)+tuple(data)
                data1=dict_data
            else:
                data1=dict_data  
            cursor.close()
            #print(data1)
            return render_template('display_vid.html',data1=data1)
        return render_template('display_vid.html',data1=data1)
    else:
        return redirect(url_for('login'))

@app.route('/upload_img', methods=['GET','POST'])
def upload_img():   
    if session.get('user'):
        cursor = mydb.cursor()
        cursor.execute('select * from info where added_by = %s', (session.get('user'),))
        data = cursor.fetchall()
        #print(data)
        if request.method=='POST':
            path=os.path.dirname(os.path.abspath(__file__))
            for image in request.files.getlist('images[]'):
                image.save(os.path.join(path,'static/img/',image.filename))
                save_no_helmet_img(os.path.join(path,'static/img'+image.filename))
            data_pth= os.path.join(path,'static/No_Helmet_Img')
            filedata=os.listdir(data_pth)
            #print(filedata)
            dict_data=[(i,recognize_plate(os.path.join(data_pth,i)),session.get('user')) for i in filedata]
            #print(dict_data)
            cursor = mydb.cursor()
            for i, j, k in dict_data:
                cursor.execute('insert into info values(%s, %s, %s)',(i, j, k))
            #cursor.executemany('insert into info values(%s, %s, %s)', dict_data)
                mydb.commit()
            cursor.execute('select * from info where added_by = %s', (session.get('user'),))
            data = cursor.fetchall()
            #print(data)
            if data[0]!=('None',):
                #data=tuple(dict_data)+tuple(data)
                data=dict_data
            else:
                data=dict_data  
            cursor.close()
            #print(data)
            return render_template('display_img.html',data=data)
        return render_template('display_img.html',data=data)
    else:
        return redirect(url_for('login'))

@app.route('/create_dataset', methods=['POST', 'GET'])
def create_dataset():
    if session.get('user'):
        if request.method=='POST':
            # get the number plate from the form
            number_plate = request.form['number_plate']

            # get the name from the form
            name = request.form['name']

            # get the email from the form
            email = request.form['email']
            
            cursor = mydb.cursor(buffered=True)
            
            cursor.execute('insert into plate_details values(%s, %s, %s)',[number_plate, name, email])
            mydb.commit()
            
            flash('Details added Successfully !')
            
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT * FROM plate_details')
        data = cursor.fetchall()
            
        return render_template('dataset.html', data=data)
    else:
        return redirect(url_for('login'))
    
@app.route('/delete/<lp>', methods=['GET','POST'])
def delete(lp):
    if session.get('user'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('delete from plate_details where lp=%s',[lp])
        mydb.commit()
        
        flash('Record deleted successfully!')
        
        cursor.execute('SELECT * FROM plate_details')
        data = cursor.fetchall()
        return redirect(url_for('create_dataset', data=data))
    else:
        return redirect(url_for('login'))

@app.route('/edit/<lp>', methods=['GET','POST'])
def edit(lp):
    if session.get('user'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select * from plate_details where lp=%s',[lp])
        data=cursor.fetchone()
        if request.method=='POST':
            number_plate = request.form['number_plate']
            name = request.form['name']
            email = request.form['email']
            
            cursor.execute('update plate_details set lp=%s,name=%s,email=%s where lp=%s',(number_plate,name,email,lp))
            mydb.commit()
            
            flash('Details updated Successfully !')
            
        cursor.execute('SELECT * FROM plate_details')
        data = cursor.fetchall()
        return render_template('dataset.html', data=data)
    else:
        return redirect(url_for('login'))
    

        
@app.route('/send_mail/<lp>/<filename>', methods=['GET','POST'])
def send_mail(lp,filename):
    if session.get('user'):
        if lp=="No license plates found in image." or lp=="Number Plate Text Not Recognized" or lp=="Error: Unknown Error":
            return lp
        else:
            cursor = mydb.cursor(buffered=True)
            
            cursor.execute('select * from plate_details where lp=%s',[lp])
            data=cursor.fetchone()
            try:
                
                if data[0]=='None':
                    flash('No data found for this license plate')
                #return 'No data found for this license plate'
                else:
                    path=os.path.dirname(os.path.abspath(__file__))
                    name=data[1]
                    license_plate=data[0]
                    to_email=data[2]
                    subject='Violation Alert: No Helmet'
                    body=body = f'Dear {name},\n\nThis is to inform you that a violation has been detected in your vehicle with license plate number {license_plate}. The violation is related to not wearing a helmet while driving.\n\nPlease ensure compliance with traffic rules and regulations in the future.\n\nSincerely,\nTraffic Violation Monitoring System'
                    attachment=os.path.join(path,'static/No_Helmet_Img',filename )
                    send_email(to_email, subject, body, attachment)
                    flash('Mail sent successfully')
                    return redirect(url_for('upload_img'))
            except Exception as e:
                flash('No data found for this license plate')
                return redirect(url_for('upload_img'))
                
    else:
        return redirect(url_for('login'))
    return render_template('display_img.html')
@app.route('/logout', methods=['GET','POST'])
def logout():
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        
        cursor.execute('select image_name from info where added_by=%s',[session.get('user')])
        data=cursor.fetchall()
        path=os.path.dirname(os.path.abspath(__file__))
        
        for i in data:
            if os.path.exists(os.path.join(os.path.join(path,'static/No_Helmet_Img',i[0]))):
                os.remove(os.path.join(path,'static/No_Helmet_Img',i[0]))
                cursor.execute('delete from info where image_name=%s',[i[0]])
                mydb.commit()
                
        cursor.execute('select image_name from info2 where added_by=%s',[session.get('user')])
        data1=cursor.fetchall()
        
        for i in data1:
            if os.path.exists(os.path.join(os.path.join(path,'static/No_Helmet',i[0]))):
                os.remove(os.path.join(path,'static/No_Helmet',i[0]))
                cursor.execute('delete from info2 where image_name=%s',[i[0]])
                mydb.commit()
                
        img_path=os.listdir(os.path.join(path,'static/img'))
        for i in img_path:
            if os.path.exists(os.path.join(os.path.join(path,'static/img',i))):
                os.remove(os.path.join(path,'static/img',i))
        
        person_bike_path = os.listdir(os.path.join(path,'static/Person_Bike'))
        for i in person_bike_path:
            if os.path.exists(os.path.join(os.path.join(path,'static/Person_Bike',i))):
                os.remove(os.path.join(path,'static/Person_Bike',i))
                
        video_path = os.listdir(os.path.join(path,'static/video'))
        for i in video_path:
            if os.path.exists(os.path.join(os.path.join(path,'static/video',i))):
                os.remove(os.path.join(path,'static/video',i))
                
        session.pop('user')
    return redirect(url_for('login'))

# Route for deleting files and records for img_upload
@app.route('/delete_img', methods=['POST', 'GET'])
def delete_img():
    if request.method == 'POST':
        cursor=mydb.cursor(buffered=True)
        cursor.execute('SELECT image_name FROM info WHERE added_by = %s', [session.get('user')])
        data = cursor.fetchall()
        path = os.path.dirname(os.path.abspath(__file__))

        for i in data:
            img_path = os.path.join(path, 'static/img', i[0])
            no_helmet_img_path = os.path.join(path, 'static/No_Helmet_Img', i[0])
            if os.path.exists(img_path):
                os.remove(img_path)
            if os.path.exists(no_helmet_img_path):
                os.remove(no_helmet_img_path)
            cursor.execute('DELETE FROM info WHERE image_name = %s', [i[0]])
            mydb.commit()

        flash('Files and records deleted successfully!', 'success')
        return redirect(url_for('upload_img'))
    else:
        # Redirect to the appropriate page or return an error message
        return 'Method Not Allowed'

# Route for deleting files and records for vid_upload
@app.route('/delete_vid', methods=['POST', 'GET'])
def delete_vid():
    if request.method == 'POST':
        cursor=mydb.cursor(buffered=True)
        cursor.execute('SELECT image_name FROM info2 WHERE added_by = %s', [session.get('user')])
        data1 = cursor.fetchall()
        
        path = os.path.dirname(os.path.abspath(__file__))

        for i in data1:
            img_path = os.path.join(path, 'static/video', i[0])
            no_helmet_img_path = os.path.join(path, 'static/No_Helmet', i[0])
            person_bike_path = os.path.join(path, 'static/Person_Bike', i[0])
            if os.path.exists(img_path):
                os.remove(img_path)
            if os.path.exists(no_helmet_img_path):
                os.remove(no_helmet_img_path)
            if os.path.exists(person_bike_path):
                os.remove(person_bike_path)

            cursor.execute('DELETE FROM info2 WHERE image_name = %s', [i[0]])
            mydb.commit()

        flash('Files and records deleted successfully.', 'success')
        return redirect(url_for('upload_vid'))


if __name__ == '__main__':
    app.run(debug=True,use_reloader=True)