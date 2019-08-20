from flask import render_template, flash, redirect, request, url_for, jsonify
from flask_login import login_user
from . import auth
from .forms import LoginForm
from ..models import User
import re
import random


# prepare for Andriod APP
@auth.route('/login', methods=['POST'])  # 用电话号码或邮箱登录，不能用用户名登录，因为用户名不唯一
def login():
    value = request.form['user']    # 获取电话号码或邮箱
    password = request.form['password']
    if re.match(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$', value):   # 判断是否为邮箱
        key = 'email'
    elif re.match(r'^(?:\+?86)?1(?:3\d{3}|5[^4\D]\d{2}|8\d{3}|7(?:[01356789]\d{2}|4(?:0\d|1[0-2]|9\d))|9[189]\d{2}|6[567]\d{2}|4[579]\d{2})\d{6}$', value):  # 判断是否为电话号码
        key = 'phone_number'
    else:
        return jsonify({'isSuccess': False, 'msg': '请输入邮箱或手机号'})
    user = User()
    if not user.get_user(key, value):
        return jsonify({'isSuccess': False, 'msg': '您还未注册'})
    if not 6 <= len(password) <= 20:
        return jsonify({'isSuccess': False, 'msg': '密码长度必须在 6 ~ 20 之间'})
    if not re.match(r'^\w{6,20}$', password):
        return jsonify({'isSuccess': False, 'msg': '密码必须由字母、数字、下划线组成'})
    if not user.verify_password(password):
        return jsonify({'isSuccess': False, 'msg': '密码错误'})
    else:
        return jsonify({'isSuccess': True})


# prepare for Andriod APP
@auth.route('/register', methods=['POST'])   # 用邮箱注册
def register():
    try:
        email = re.match(
            r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$', request.form['email']).group()
    except:
        return jsonify({'isSuccess': False, 'msg': '电子邮件格式不正确'})
    user = User()
    if user.get_user("email", email) > 0:
        return jsonify({'isSuccess': False, 'msg': '该邮箱已被注册'})
    password = request.form['password']
    if not 6 <= len(password) <= 20:
        return jsonify({'isSuccess': False, 'msg': '密码长度必须在 6 ~ 20 之间'})
    if not re.match(r'^\w{6,20}$', password):
        return jsonify({'isSuccess': False, 'msg': '密码必须由字母、数字、下划线组成'})
    if user.add_user(email, password) != 1:
        return jsonify({'isSuccess': False, 'msg': '系统内部错误'})
    return jsonify({'isSuccess': True})


# prepare for web
@auth.route('/_login', methods=['GET', 'POST'])
def _login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User()
        if user.get_user("email", form.email.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid email or password.')
    return render_template('login.html', form=form)
