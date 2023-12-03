from flask import Flask,send_file,request,jsonify,make_response,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
import uuid
import automail
from threading import Thread,Event
import atexit
import pathlib
import os
import bgremover
import video_enhance as ven
from colorize import colorizePhoto
import string
import random
import configuration

app = Flask(__name__)

bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'

def encode_auth_token():
    ramdomUUID = uuid.uuid1()
    return ramdomUUID

db = SQLAlchemy(app)
usage_token = encode_auth_token()

def refresh_token():
    usage_token = encode_auth_token() 
    
def generateVerifyCode():
    random_uuid  = uuid.uuid4()
    random_uuid = str(random_uuid)
    return random_uuid[0:6]

TYPE_ENHANCE = 0
TYPE_REMOVE_BG = 1
TYPE_COLORIZE = 2
TYPE_VIDEO = 3

class SavedImage(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key= True)
    file_name = db.Column(db.String(200), nullable = False)
    username = db.Column(db.String(20), nullable = False)
    type = db.Column(db.Integer, default = 0)
    absolute_path = db.Column(db.String(200), nullable = False)
    
    def __init__(self, file_name, username, type, absolute_path):
        self.file_name = file_name
        self.username = username
        self.type = type
        self.absolute_path = absolute_path
        
    def __str__(self):
        return f"file_name: {self.file_name}"
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class UnverifiedUser(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    fullname = db.Column(db.String(40),nullable= False)
    email = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    verify_code : str = db.Column(db.String(10), nullable = False)
    verified = db.Column(db.Boolean(), default = False)
    
    def __init__(self,username,email,fullname,password):
        self.username = username
        self.email = email
        self.fullname = fullname
        self.password = password
        
    def set_verify_code(self,code):
        self.verify_code = code
        
    def verify_account(self,code : str):
        if (self.verify_code == code):
            self.verified = True
            return True       
        return False
    
    def set_password_and_valid_account(self):
        hash_password = bcrypt.generate_password_hash(password = self.password).decode('utf-8')
        t_user = User(username=self.username,email=self.email,password=hash_password,fullname=self.fullname)
        db.session.add(t_user)
        db.session.commit()          

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    fullname = db.Column(db.String(40),nullable= False)
    email = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    
    
    def __init__(self,username,email,password,fullname):
        self.username = username
        self.password = password
        self.email = email
        self.fullname = fullname    
        
    def check_password(self,password):
        return bcrypt.check_password_hash(self.password,password)
      
with app.app_context():
    db.create_all()
    
def listen_destroy_event():
    try:
        print("Destroyed")
        automail.quit()
    except:
        pass
        
    
@app.route('/')
def home():
    return "Welcome to Dashboard" 

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        t_username = request.json['username']
        t_password = request.json['password']
        
        user = User.query.filter_by(username = t_username).first()
        if user and user.check_password(password = t_password):
            
            result = [{'result': 1,'username' : t_username,'email' : user.email,'fullname' : user.fullname, 'message': 'Success', 'token' : usage_token}]
            return make_response(jsonify(result),200)
        else:
            result = [{'result': 0, 'message': 'Username or password incorrect'}]
            return make_response(jsonify(result),201)
    elif request.method == 'GET':
        return "Nothing here"
    
def sendRequestVerifyEmail(user : UnverifiedUser):
    target =[user.email]
    automail.send_email(target = target, msg = automail.buid_msg_content(text_message=user.verify_code))

@app.route('/register1', methods=['GET','POST'])
def register1():
    if request.method == 'POST':
        
        t_username = request.json['username']
        t_email = request.json['email']

        
        if validate_exist_username(t_username= t_username):
            result = [{'result': 1, 'message': 'Success'}]
            if validate_exist_email(t_email = t_email):
                
                # verifyCode = generateVerifyCode()
                # t_user_unverified = UnverifiedUser(username = t_username, email= t_email, fullname = t_fullname)
                # t_user_unverified.set_verify_code(code= verifyCode)
            
                # hash_password = bcrypt.generate_password_hash(password= t_password).decode('utf-8')
                # t_user = User(t_username,t_email,hash_password)
                # db.session.add(t_user_unverified)
                # db.session.commit()
                
                # sendRequestVerifyEmail(t_user_unverified)
               
                #Just notice client that email and username is valid, then client go to set password
                return make_response(jsonify(result),200)  
            else:
                result = [{'result': 0, 'message': 'Email already used'}] 
        else:
            message = "Username already existed"
            result = [{'result': 0, 'message': message}] 
           
        return make_response(jsonify(result),201)

    elif request.method == 'GET':
        return "Nothing available"   
    
@app.route('/register2', methods=['GET','POST'])
def register2():
    if request.method == 'POST':
        
        t_username = request.json['username']
        t_email = request.json['email']
        t_fullname = request.json['fullname']
        t_password = request.json['password']

        
        if validate_exist_username(t_username= t_username):
            result = [{'result': 1, 'message': 'Success'}]
            if validate_exist_email(t_email = t_email):
                
                verifyCode = generateVerifyCode()
                
                user_unverified_exist = validate_exist_unverified_user(t_email= t_email)   
                user_unverified_exist2 = db.session.query(UnverifiedUser).filter_by(username=t_username).first()
                try:
                    if user_unverified_exist:
                        db.session.delete(user_unverified_exist)
                        db.session.commit()
                    if user_unverified_exist2:
                        db.session.delete(user_unverified_exist2)
                        db.session.commit()
    
                except:
                    print("Conflic error")
                
                
                t_user_unverified = UnverifiedUser(username = t_username, email= t_email, fullname = t_fullname, password= t_password)
                t_user_unverified.set_verify_code(code= verifyCode)
                # hash_password = bcrypt.generate_password_hash(password= t_password).decode('utf-8')
                # t_user = User(t_username,t_email,hash_password)
                db.session.add(t_user_unverified)
                db.session.commit()
                
                sendRequestVerifyEmail(t_user_unverified)
               
                #Just notice client that email and username is valid, then client go to set password
                return make_response(jsonify(result),200)  
            else:
                result = [{'result': 0, 'message': 'Email already used'}] 
        else:
            message = "Username already existed"
            result = [{'result': 0, 'message': message}] 
           
        return make_response(jsonify(result),400)

    elif request.method == 'GET':
        return "Nothing available" 
    
def processImage(path):
    oldname = pathlib.Path(path).name
    newpath = configuration.ENHANCE_FACE_RES_DIR

    cmdExec = "python D:\hoctap\Python\GFPGAN\inference_gfpgan.py -i " + str(path) + " -o " + newpath + " -v 1.3 -s 2"
    os.system(cmdExec)
    
    return os.path.join(newpath + "\\restored_imgs", oldname)

@app.route('/image', methods=['GET'])
def get_image_with_url():
    name = request.args.get('name',default="thanh.jpg", type = str)
    type = request.args.get('type', default=TYPE_ENHANCE, type = int)
    
    if type == TYPE_ENHANCE:
        parent = configuration.ENHANCE_FACE_RESTORED_DIR
        true_path = os.path.join(parent,name)
        if os.path.isfile(true_path):
            return send_file(true_path,mimetype='image/gif')
        else:
            return "Image not found"
    elif type == TYPE_REMOVE_BG:
        parent = configuration.REMOVE_BG_RESULT_DIR
        true_path = os.path.join(parent,name)
        if os.path.isfile(true_path):
            return send_file(true_path,mimetype='image/gif')
        else:
            return "Image not found"
    elif type == TYPE_COLORIZE:
        parent = configuration.COLORIZE_RESULT_DIR
        true_path = os.path.join(parent,name)
        if os.path.isfile(true_path):
            return send_file(true_path,mimetype='image/gif')
        else:
            return "Image not found"
    elif type == TYPE_VIDEO:
        parent = configuration.ENHANCE_VIDEO_RES_DIR  
        true_path = os.path.join(parent,name)
        if os.path.isfile(true_path):
            return send_file(true_path,mimetype='video/mp4')
        else:
            return "Video not found"

@app.route('/my&image.py', methods=['GET','POST'])
def get_saved_images():
    if request.method == 'POST':
        t_token = request.json['token']
        t_username = request.json['username']
        
        if (True):
            saved_list = SavedImage.query.filter_by(username = t_username).all()
            
            res_list = []
            for row in saved_list:
                res_list.append(row.as_dict())
            return make_response(jsonify(res_list),200)
        else:
            return "Bad token"
    return "Unvailable"

@app.route('/video&enhance.py', methods = ['GET','POST'])
def enhance_video():
    if request.method == 'POST':
        if 'file1' not in request.files:
            return 'there is no file in form!'
        t_file1 = request.files['file1']
        
        t_token = request.form.get('token')
        t_username = request.form.get('username')
        t_session_id= request.form.get('session_id')
        
        if (True):
            t_filename =  "ve_" + t_file1.filename
            path = os.path.join(configuration.ENHANCE_VIDEO_INPUT_DIR, t_filename)
            t_file1.save(path)
            
            dir = configuration.ENHANCE_VIDEO_RESTORED_DIR
            
            out_file_name = str(uuid.uuid4()) + ".mp4"
            output = os.path.join(dir, out_file_name)
            
            outfile = ven.enhanceVideo(input_path= path, output_path= output)
            
            savedImage = SavedImage(file_name= out_file_name, username = t_username, type= TYPE_VIDEO, absolute_path= outfile)
            db.session.add(savedImage)
            db.session.commit()
            
            return send_file(outfile, mimetype='video/mp4')
        else:
            return "Bad token"

@app.route('/colorize.py', methods=['GET','POST'])
def colorize_img():
    if request.method == 'POST':
        if 'file1' not in request.files:
            return 'there is no file in form!'
        t_file1 = request.files['file1']
        
        t_token = request.form.get('token')
        t_username = request.form.get('username')
        t_session_id= request.form.get('session_id')
        
        if (True):
            t_filename =  "colorize_" + t_file1.filename
            path = os.path.join(configuration.COLORIZE_RES_DIR , t_filename)
            t_file1.save(path)
            
            dir = configuration.COLORIZE_RESULT_DIR
            out_file_name = str(uuid.uuid4()) + ".png"
            output = os.path.join(dir, out_file_name)
            
            outfile = colorizePhoto(input = path, output= output)
            
            savedImage = SavedImage(file_name= out_file_name, username = t_username, type= TYPE_COLORIZE, absolute_path= outfile)
            db.session.add(savedImage)
            db.session.commit()
            
            return send_file(outfile, mimetype='image/gif')
        else:
            return "Bad token"

@app.route('/bg&remove.py', methods=['GET','POST'])
def remove_bg():
    if request.method == 'POST':
        if 'file1' not in request.files:
            return 'there is no file1 in form!'
        t_file1 = request.files['file1']
            
        t_token = request.form.get('token')
        t_username = request.form.get('username')
        t_session_id= request.form.get('session_id')
        
        if (True):
            t_filename = t_session_id + "_rembg_" + t_file1.filename
            path = os.path.join(configuration.REMOVE_BG_INPUT_DIR, t_filename)
            t_file1.save(path)
            
            outfile = os.path.join(configuration.REMOVE_BG_RESULT_DIR, t_filename)
            bgremover.remove_bg(i_path= path, o_path = outfile)
            
            savedImage = SavedImage(file_name= t_filename, username = t_username, type= TYPE_REMOVE_BG, absolute_path= outfile)
            db.session.add(savedImage)
            db.session.commit()
            
            return send_file(outfile, mimetype='image/gif')
        else:
            return "Bad token"
    else:
        return " No such file"   
    
@app.route('/enhance.py',methods=['GET','POST'])
def enhance_image():
    if request.method == 'POST':
        if 'file1' not in request.files:
            return 'there is no file1 in form!'
        t_file1 = request.files['file1']
        
        t_token = request.form.get('token')
        t_username = request.form.get('username')
        t_session_id= request.form.get('session_id')
        
        if (True):
          
            t_filename = t_session_id + t_file1.filename
            path = os.path.join(configuration.ENHANCE_FACE_RES_DIR, t_filename)
            t_file1.save(path)
            

            output_path = processImage(path)
            savedImage = SavedImage(file_name= t_filename, username = t_username, type= TYPE_ENHANCE, absolute_path= output_path)
            db.session.add(savedImage)
            db.session.commit()

            return send_file(output_path, mimetype='image/gif')
            
        else:
            return "Bad token"

      
    return "No file selected"

@app.route('/forgot_password', methods=['GET','POST'])
def forgot_password():
    if request.method == 'POST':
        # get email from request
        t_email = request.json['email']
        
        # query user by email
        exist_email = User.query.filter_by(email = t_email).first()
        
        #check if email exist in database or not
        if(exist_email):
            # create target to send email automatically
            target =[exist_email.email]
    
            # generate new random password
            m_new_password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            # hash it by bcrypt
            new_hash_pw = bcrypt.generate_password_hash(password = m_new_password).decode('utf-8')
            
            # make message for email
            m_text_msg = "Your new password: " + m_new_password
            
            #update new hashed password to database
            exist_email.password = new_hash_pw
            db.session.commit()
            
            #send email with message contain new visible password
            automail.send_email(target = target, msg = automail.buid_msg_content(text_message=m_text_msg))
            
            #return response
            response1 = [{'result': 1, 'message': 'Success'}]
            return make_response(jsonify(response1),200)
        else:
            response2 = [{'result': 0, 'message': 'Email not registerd yet'}]
            return make_response(jsonify(response1),201)
        
    else:
        return "Nothing to get"
                 
@app.route('/register/verify', methods=['GET','POST'])
def verify_email():
    if request.method == 'POST':
    
        t_email = request.json['email']
        t_code = request.json['code']
        
        unv_user = validate_exist_unverified_user(t_email= t_email)
        
        #check valid username
        if validate_exist_username(t_username= unv_user.username):
            response1 = [{'result': 1, 'message': 'Success'}]
            
            #check valid email
            if validate_exist_email(t_email = t_email):
                #check_email_unverified_exist
                if unv_user:
                    result = unv_user.verify_account(code= t_code)
                    #check_verify_code
                    if result:
                        unv_user.set_password_and_valid_account()
                        db.session.delete(unv_user)
                        db.session.commit()
                        response1 = [{'result': 1, 'message': 'Success'}]
                        return make_response(jsonify(response1),200)
                    else:
                        message = "Verify code incorrect"
                        response1 = [{'result': 0, 'message': message}] 
    
                return make_response(jsonify(response1),400)  
            else:
                response1 = [{'result': 2, 'message': 'Email already used'}] 
        else:
            message = "Username already existed"
            response1 = [{'result': 3, 'message': message}] 
        return make_response(jsonify(response1),400)    
            

    elif request.method == 'GET':
        return "Nothing available" 

    
def validate_exist_email(t_email):
    exist_email = User.query.filter_by(email = t_email).first()
    if exist_email:
        return False
    return True       
    
def validate_exist_username(t_username):
    exist_username = User.query.filter_by(username = t_username).first()
    if exist_username:
        return False
    return True

def validate_exist_unverified_user(t_email) -> UnverifiedUser:
    return UnverifiedUser.query.filter_by(email = t_email).first()
   
        
            
class MyThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(86400):
            refresh_token()


if __name__ == '__main__':
    stopFlag = Event()
    thread = MyThread(stopFlag)
    thread.start()
    atexit.register(listen_destroy_event)
    app.run(host="0.0.0.0", port=5000, debug=True)
    
