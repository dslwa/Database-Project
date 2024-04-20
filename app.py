from flask import Flask, render_template, url_for, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask (__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
db = SQLAlchemy(app)

class Customers(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    email = db.Column(db.String(100), nullable=False, default='unknown@example.com')
    phone = db.Column(db.String(10), nullable=False, default='N/A')
    def __repr__(self):
        return '<Customer % r>' % self.id

class Orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'))
    product = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    customer = db.relationship('Customers', backref='orders')
    def __repr__(self):
        return '<Order % r>' % self.id


@app.route('/',methods=['POST', 'GET'])
def homepage():
    return render_template('index.html')

@app.route('/customer', methods=['POST', 'GET'])
def customers():
    if request.method == 'POST':
        if 'fill_table' in request.form:
            sample_data = {
                'customer_id': 123,
                'name': 'Sample name',
                'email': 'ex@gmail.com',
                'phone': 545432132
            }
            return render_template('customers.html', sample_data=sample_data)

        elif 'add_customer' in request.form:
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')

            new_customer = Customers(name=name, email=email, phone=phone)
            db.session.add(new_customer)
            db.session.commit()

    customers_data = Customers.query.all()
    return render_template('customers.html', customers_data=customers_data)

@app.route('/customer/delete/<int:customer_id>')
def delete_customer(customer_id):
    row_to_delete = Customers.query.get_or_404(customer_id)

    try:
        db.session.delete(row_to_delete)
        db.session.commit()
        return redirect('/customer')
    except:
        return 'There is an issue'

@app.route('/customer/update/<int:customer_id>', methods=['GET', 'POST'])
def update_customer(customer_id):
    customer = Customers.query.get_or_404(customer_id)

    if request.method == 'POST':
        customer.name = request.form.get('name')
        customer.email = request.form.get('email')
        customer.phone = request.form.get('phone')
        db.session.commit()
        return redirect('/customer')
    else:
        return render_template('updateCustomer.html', customer=customer, customer_id=customer_id)

@app.route('/order', methods=['POST', 'GET'])
def orders():
    if request.method == 'POST':
        if 'fill_table' in request.form:
            sample_data = {
                'order_id': 1,
                'customer_id': 123,
                'product': 'Sample Product',
                'quantity': 5,
                'order_date': datetime.now()
            }
            return render_template('order.html', sample_data=sample_data)

        elif 'add_order' in request.form:
            customer_id = request.form.get('customer_id')
            product = request.form.get('product')
            quantity = request.form.get('quantity')
            order_date = datetime.now()

            new_order = Orders(customer_id=customer_id, product=product, quantity=quantity, order_date=order_date)
            db.session.add(new_order)
            db.session.commit()

    orders_data = Orders.query.all()
    return render_template('order.html', orders_data=orders_data)


@app.route('/order/delete/<int:order_id>')
def delete(order_id):
    row_to_delete = Orders.query.get_or_404(order_id)

    try:
        db.session.delete(row_to_delete)
        db.session.commit()
        return redirect('/order')
    except:
        return 'There is an issue'


@app.route('/order/update/<int:order_id>', methods=['GET', 'POST'])
def update(order_id):
    order = Orders.query.get_or_404(order_id)

    if request.method == 'POST':
        order.customer_id = request.form.get('customer_id')
        order.product = request.form.get('product')
        order.quantity = request.form.get('quantity')
        db.session.commit()
        return redirect('/order')
    else:
        return render_template('updateOrder.html', order=order, order_id=order_id)

@app.route('/join')
def join_tables():
    join_type = request.args.get('join_type', 'inner')  
    
    if join_type == 'inner':
        joined_data = db.session.query(Customers, Orders).filter(Customers.customer_id == Orders.customer_id).all()
    elif join_type == 'left1':
        joined_data = db.session.query(Customers, Orders).outerjoin(Orders, Customers.customer_id == Orders.order_id).all()
    elif join_type == 'left2':
        joined_data = db.session.query(Customers, Orders).outerjoin(Customers, Orders.order_id == Customers.customer_id).all()
    else:
        return "Invalid join type"

    return render_template('join_result.html', joined_data=joined_data, join_type=join_type)

with app.app_context():
    db.create_all()



if __name__ == "__main__":
    app.run(debug=True)