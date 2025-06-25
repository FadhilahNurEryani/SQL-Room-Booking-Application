from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, DateField, SelectField, SubmitField
from wtforms.validators import InputRequired, Length, Regexp, EqualTo, ValidationError
from flask_bootstrap import Bootstrap
from passlib.hash import pbkdf2_sha256
from datetime import date, datetime
from jinja2.exceptions import TemplateNotFound
from dateutil.relativedelta import relativedelta
from markupsafe import Markup
from flask_msearch import Search




folderPath = os.path.dirname(os.path.abspath(__file__))


app = Flask(__name__)
Bootstrap(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + folderPath + "/master.db"
app.config["SECRET_KEY"] = 'zR11b652Ue6tMD8SavPNvxk9EFJ5i7jZ'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login dulu kak'
search = Search()
search = Search(db=db)
search.init_app(app)
search.create_index(update=True)
MSEARCH_INDEX_NAME = 'msearch'
MSEARCH_ENABLE = True
MSEARCH_BACKEND = 'whoosh'



def checkusername(form, field):
    usercheck = users.query.filter_by(username=form.username.data).first()
    if usercheck:
       raise ValidationError("Username already exists. Select a different username")
    
def loginCheck(form,field):
   usernamecheck = users.query.filter_by(username=form.username.data).first()
   if usernamecheck is None:
      raise ValidationError('Username or password is incorrect')
   elif not pbkdf2_sha256.verify(field.data, usernamecheck.password):
      raise ValidationError('Username or password is incorrect')

def bookingCheck(form, field):
    roomnum = session.get('roomnum')
    print("Room number:", roomnum)
    slotValues = ['9:00 AM - 10:00 AM','10:00 AM - 11:00 AM','11:00 AM - 12:00 PM','12:00 PM - 1:00 PM','1:00 PM - 2:00 PM','2:00 PM - 3:00 PM']
    bookedSlots = []
    slotNames = []

    for slotValue in slotValues:
        bookingExists = book.query.filter_by(roomID=roomnum, datebooked=form.date.data, timeSlot=slotValue).all()
        if bookingExists:
          bookedSlots.append(slotValue)
          
    for field_name, field_obj in form._fields.items():
        for bookedSlot in bookedSlots:
            if field_name.startswith('slot') and field_obj.label.text == bookedSlot:
                slotNames.append(field_name)
    
    for slotValue in slotValues:
        bookingExists = book.query.filter_by(roomID=roomnum, datebooked=form.date.data, timeSlot=slotValue).all()
        if bookingExists:
          for slotName in slotNames:
            slotField = getattr(form, slotName)
            slotField.render_kw = {'style': 'display: none;'} 
            slotField.label.text = ''


def noneSelected(form,field):
    selectedSlots = []
  
    for field_name, field in form._fields.items():
        if field_name.startswith('slot') and field.data:
            selectedSlots.append(field.label.text)

    if not selectedSlots:
        flash("Please select at least one time slot.")

def bookingLimit(form,field):
    roomnum = session.get('roomnum')
    bookingExists = book.query.filter_by(roomID=roomnum, datebooked=form.date.data, userID=current_user.id).first()
    userRoleCheck = users.query.filter_by(id=current_user.id).first()
    role = userRoleCheck.role
    if bookingExists and role == 'Student':
        flash("Sorry you can only book a certain room once a day, please book on another date")
        raise ValidationError('Booking Limit Reached')

def bookingAuth(form,field):
    roomnum = session.get('roomnum')
    roomType = rooms.query.filter_by(number=roomnum).first()
    if roomType:
        auth = roomType.auth
        if auth == 1 and current_user.role == 'Student':
            flash("Sorry you don't have permission to book this room")
            raise ValidationError('Booking Denied, Not Authorised')

def monthLimit(form, field):
    dateCheck = book.query.filter_by(userID=current_user.id).all()
    userRoleCheck = users.query.filter_by(id=current_user.id).first()
    selectedDate = session.get('sessionDate')
    datesList = []
    if dateCheck:
        role = userRoleCheck.role
        selectedMonth = datetime.strptime(selectedDate,'%Y-%m-%d').strftime('%Y-%m')

        for booking in dateCheck:
            checkMonth = datetime.strptime(booking.datebooked,'%Y-%m-%d').strftime('%Y-%m')
            datesList.append(checkMonth)

        monthCount = datesList.count(selectedMonth)
        
        if monthCount >= 8 and role == 'Student':
            flash('You have reached your monthly booking limit of 8')
            raise ValidationError('Monthly Booking Limit Reached')


def teacherLimit(form, field):
    roomnum = session.get('roomnum')
    dateCheck = book.query.filter_by(userID=current_user.id,roomID=roomnum).all()
    userRoleCheck = users.query.filter_by(id=current_user.id).first()
    selectedDate = session.get('sessionDate')
    datesList = []
    if dateCheck:
        role = userRoleCheck.role
        selectedDay = datetime.strptime(selectedDate,'%Y-%m-%d').strftime('%Y-%m-%d')

        for booking in dateCheck:
            checkDay = datetime.strptime(booking.datebooked,'%Y-%m-%d').strftime('%Y-%m-%d')
            datesList.append(checkDay)

        dayCount = datesList.count(selectedDay)
        
        if dayCount >= 3 and role == 'Teacher':
            flash('You cannot book a single room more than three times in a day, please book on another date')
            raise ValidationError('Daily Booking Limit Reached')
        

def oldpword(pform,field):
   usernamecheck = users.query.filter_by(username=current_user.username).first()
   if not pbkdf2_sha256.verify(field.data, usernamecheck.password):
      raise ValidationError('Password entered is incorrect please enter correct current password')




class users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), unique=True)
    password = db.Column(db.String(100))
    dob = db.Column(db.String)
    role = db.Column(db.String)
    


class rooms(db.Model):
    __tablename__ = 'rooms'
    __searchable__ = ['number','location','desks','type']

    number = db.Column(db.String, unique=True, primary_key=True)
    location = db.Column(db.String)
    desks = db.Column(db.Integer)
    type = db.Column(db.String)
    auth = db.Column(db.Integer)

    


class book(db.Model):
    bookingID = db.Column(db.Integer, unique=True, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    roomID = db.Column(db.String, db.ForeignKey('rooms.number'))
    datebooked = db.Column(db.String)
    timeSlot = db.Column(db.String)



class loginform(FlaskForm):
    username = StringField('Username', validators=[InputRequired(),Length(min=5,max=12)], render_kw={"placeholder": "Enter your username"})
    password = PasswordField('Password', validators=[InputRequired(),Length(min=8,max=50),loginCheck], render_kw={"placeholder": "Enter your password"})
    remember = BooleanField('Remember me')

class registerform(FlaskForm):
    username = StringField('Username', validators=[InputRequired(),Length(min=5,max=12),Regexp('^\w+$', message="Username must contain only letters numbers or underscores"),checkusername] , render_kw={"placeholder": "Create username"})
    password = PasswordField('Password', validators=[InputRequired(),Length(min=8,max=50),EqualTo('confirm', message='Passwords must match')], render_kw={"placeholder": "Create password"})
    confirm  = PasswordField('Repeat Password', validators=[InputRequired(),Length(min=8,max=50)], render_kw={"placeholder": "Confirm Password"})
    dob = DateField('Date of Birth', validators=[InputRequired()],render_kw={'max': date.today() - relativedelta(years=15)})
    role = SelectField(u'Role', choices=[('Student'), ('Teacher')], validators=[InputRequired()])

class bookingform(FlaskForm):
    date = DateField('Booking Date',  validators=[InputRequired()], default=date.today(), render_kw={'min': date.today(),'max': date.today() + relativedelta(months=1),})
    slot1 = BooleanField('9:00 AM - 10:00 AM')
    slot2 = BooleanField('10:00 AM - 11:00 AM')
    slot3 = BooleanField('11:00 AM - 12:00 PM')
    slot4 = BooleanField('12:00 PM - 1:00 PM')
    slot5 = BooleanField('1:00 PM - 2:00 PM')
    slot6 = BooleanField('2:00 PM - 3:00 PM')
    submit = SubmitField('Book',validators=[noneSelected,bookingCheck,bookingLimit,bookingAuth,monthLimit,teacherLimit])
    
class settingsform(FlaskForm):
    username = StringField('Username', validators=[InputRequired(),Length(min=5,max=12),Regexp('^\w+$', message="Username must contain only letters numbers or underscores"),checkusername] , render_kw={"placeholder": "Change username"})
    dob = DateField('Date of Birth',render_kw={'disabled':''} )
    role = StringField('Role',render_kw={'disabled':''})
    submit = SubmitField('Save Changes')

class passwordform(FlaskForm):
    oldpassword = PasswordField('Old Password', validators=[InputRequired(),Length(min=8,max=50),oldpword], render_kw={"placeholder": "Old Password"})
    newpassword = PasswordField('New Password', validators=[InputRequired(),Length(min=8,max=50),EqualTo('confirm', message='New Passwords Must Match')], render_kw={"placeholder": "Create New Password"})
    confirm  = PasswordField('Repeat Password', validators=[InputRequired(),Length(min=8,max=50)], render_kw={"placeholder": "Confirm New Password"})
    submit = SubmitField('Change Password')

class deleteform(FlaskForm):
    delpassword = PasswordField('Password', validators=[InputRequired(),Length(min=8,max=50),oldpword], render_kw={"placeholder": "Enter Your Password"})
    deleteaccount = SubmitField('Delete Account')




@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))



today = date.today()
@app.route('/')
@login_required
def index():
    d2 = today.strftime("%B %d, %Y")
    bookings = book.query.filter_by(userID=current_user.id)
    currentDate = datetime.today().date()
    upcomingBookings = []
    for booking in bookings:
        bookingDate = datetime.strptime(booking.datebooked,'%Y-%m-%d').date()
        if bookingDate >= currentDate:
            upcomingBookings.append(booking)
        upcomingBookings.sort(key=lambda x: datetime.strptime(x.datebooked, '%Y-%m-%d').date())
        upcomingBookings = upcomingBookings[:4]
    return render_template('index.html', name=current_user.username, dob=current_user.dob, day=d2,bookings=upcomingBookings)



@app.route('/booking', methods=['GET','POST'])
@login_required
def booking():
    selectedloc = request.args.get('location')
    searchquery = request.args.get('query')
    desksort = request.args.get('desksort')

    if selectedloc is None:
        selectedloc = ''
    if selectedloc:
        room = rooms.query.filter_by(location=selectedloc)
    else:
        room = rooms.query

    if desksort == 'desc':
        room = room.order_by(rooms.desks.desc())
    else:
        room = room.order_by(rooms.desks)

    if searchquery: 
        searchterms = searchquery.split()
        searchterms = [term for term in searchterms if term.lower() not in ['desk', 'desks']]
        searchquery = ' '.join(searchterms)

        room = rooms.query.msearch(searchquery, fields=['number','location','desks','type']).filter()
        flash(f'Search Query: {searchquery}' )
        

    room = room.all()  
    return render_template('booking.html', room=room, selectedloc=selectedloc, desksort=desksort, searchquery=searchquery)


@app.route('/rooms/<roomnum>', methods=['GET','POST'])
@login_required
def book_room(roomnum):
    form = bookingform()
    
    if 'roomnum' in session:
        del session['roomnum'] 
    session['roomnum'] = roomnum

  
    bookingCheck(form, None)

    if form.validate_on_submit():
        selectedSlot = None
        for field_name, field in form._fields.items():
            if field_name.startswith('slot') and field.data:
                selectedSlot = field.label.text
                break

        if selectedSlot:
           newBooking = book(userID=current_user.id, roomID=roomnum, datebooked=form.date.data, timeSlot=selectedSlot)
           db.session.add(newBooking)
           db.session.commit() 
           flash(Markup(f'Booking Sucessful for Room {roomnum} on {form.date.data}, Click <a href="/mybookings" class="alert-link">here</a> to view all your Bookings'))
           return redirect(url_for('book_room', roomnum=roomnum))
           

    roomfolder = 'templates/rooms'
    if not os.path.exists(roomfolder):
        os.mkdir(roomfolder)

    room = rooms.query.filter_by(number=roomnum).first()
    if room:
        try:
            return render_template(f'{roomnum}.html', room=room, form=form)
        except TemplateNotFound:
            htmlcont = render_template('bookingtemp.html', room=room, form=form)  
            with open(f'templates/rooms/{roomnum}.html', 'w') as roomfile:
                roomfile.write(htmlcont)
            return render_template(f'rooms/{roomnum}.html')


@app.route('/updateForm', methods=['POST'])
@login_required
def booking_check():
    selectedDate = request.json['date']
    roomnum = session.get('roomnum')
    print(selectedDate)
    if 'sessionDate' in session:
        del session['sessionDate'] 
    session['sessionDate'] = selectedDate

    form = bookingform()
    bookingCheck(form, selectedDate)

    updated_form_html = render_template('bookingform.html', form=form, room=roomnum)
    
    return jsonify({'form_html': updated_form_html})




@app.route('/mybookings')
@login_required
def mybookings():
    selectedcat = request.args.get('categories')
    datesort = request.args.get('datesort')
    bookings = book.query.filter_by(userID=current_user.id)
    pastBookings = []
    upcomingBookings = []

    if selectedcat is None:
        selectedcat = ''
    
    if selectedcat == '':
        if datesort == 'desc':
            bookings = bookings.order_by(book.datebooked.desc())
        else:
            bookings = bookings.order_by(book.datebooked)  


    if selectedcat == 'past':
        today = datetime.today().date()
        for booking in bookings:
            bookingDate = datetime.strptime(booking.datebooked,'%Y-%m-%d').date()
            if bookingDate < today:
                pastBookings.append(booking)
        
        if datesort == 'desc':
            pastBookings.sort(key=lambda x: datetime.strptime(x.datebooked, '%Y-%m-%d').date(), reverse=True)
        else:
            pastBookings.sort(key=lambda x: datetime.strptime(x.datebooked, '%Y-%m-%d').date())

        return render_template('mybookings.html',bookings=pastBookings,selectedcat=selectedcat,datesort=datesort)

    if selectedcat == 'upcoming':  
        today = datetime.today().date()
        for booking in bookings:
            bookingDate = datetime.strptime(booking.datebooked,'%Y-%m-%d').date()
            if bookingDate >= today:
                upcomingBookings.append(booking)

        if datesort == 'desc':
            upcomingBookings.sort(key=lambda x: datetime.strptime(x.datebooked, '%Y-%m-%d').date(), reverse=True)
        else:
            upcomingBookings.sort(key=lambda x: datetime.strptime(x.datebooked, '%Y-%m-%d').date())

        return render_template('mybookings.html',bookings=upcomingBookings,selectedcat=selectedcat,datesort=datesort)

    return render_template('mybookings.html',bookings=bookings,selectedcat=selectedcat,datesort=datesort)


@app.route('/delete/<int:bookingID>', methods=['GET', 'POST'])
@login_required
def delete(bookingID):
    booking = book.query.get(bookingID)
    if booking:
        if booking.userID == current_user.id:
            db.session.delete(booking)
            db.session.commit()
            flash(f'Booking {bookingID} deleted successfully')
    return redirect(url_for('mybookings'))


@app.route('/reschedule/<roomID>', methods=['GET', 'POST'])
@login_required
def reschedule(roomID):
    bookingID = request.args.get('bookingID')
    if bookingID:
        booking = book.query.get(bookingID)
        if booking:
            db.session.delete(booking)
            db.session.commit()
            return redirect(url_for('book_room',roomnum=roomID,datebooked=booking.datebooked))
    return redirect(url_for('mybookings'))



@app.route('/settings',methods=['GET', 'POST'])
@login_required
def settings():
    form = settingsform()
    pform = passwordform()
    delform = deleteform()

    if form.validate_on_submit():
        user = users.query.get(current_user.id)
        if user:
           user.username = form.username.data
           db.session.commit()
           flash('Username changed successfully!')

    if pform.validate_on_submit():
        user = users.query.get(current_user.id)
        if user:
            pw_hash = pbkdf2_sha256.hash(pform.newpassword.data)
            user.password = pw_hash
            db.session.commit()
            flash('Password changed successfully!')

    if delform.validate_on_submit():
        user = users.query.get(current_user.id)
        bookings = book.query.filter_by(userID=current_user.id)
        if user:
           for booking in bookings:
              db.session.delete(booking)
           db.session.delete(user)
           db.session.commit()
           flash('Your account has been deleted sucessfully')
        return redirect(url_for('login'))
    

    return render_template('settings.html',username=current_user.username.title(),form=form,pform=pform,delform=delform)





@app.route('/login', methods = ["GET","POST"])
def login():
    logout_user()
    form = loginform()

    
    if form.validate_on_submit():
        user = users.query.filter_by(username=form.username.data).first()
        if user:
            if pbkdf2_sha256.verify(form.password.data, user.password):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('index'))
    
    return render_template('login.html', form=form)


@app.route('/register', methods = ["GET", "POST"])
def registerpage():
    logout_user()
    form = registerform()
    
    if form.validate_on_submit():
        pw_hash = pbkdf2_sha256.hash(form.password.data)
        newuser = users(username=form.username.data,password=pw_hash,dob=form.dob.data,role=form.role.data)
        db.session.add(newuser)
        db.session.commit()
        login_user(newuser)
        return redirect(url_for('index'))
           
    return render_template('register.html', form=form) 

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404


if __name__ == '__main__':
    app.run(debug=True)
