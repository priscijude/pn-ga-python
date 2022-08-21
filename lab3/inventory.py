from select import select
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
#from flask_bootstrap import Bootstrap
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')


#route to show all existing inventory
@app.route('/inventories')
def get_inventories(): #list all the existing inventory from csv file
    inventory_list = pd.read_csv('inventories.csv')
    return render_template('inventories.html', inventories = inventory_list.to_dict('records'))

#route to add a new inventory item
@app.route('/inventories/new', methods=['GET', 'POST'])
def add_new_inventory():
    if request.method == 'GET':
        return render_template('new-inventory.html')
    else:
        #read the current inventory items from file 
        inventories = pd.read_csv('inventories.csv')
        inventory_list = inventories.to_dict('records')

        #add new inventory item to list
        item_sku = request.form['sku']
        item_name = request.form['name']
        item_description = request.form['description']
        item_date = request.form['date']
        item_quantity = request.form['quantity']
        item_cost = request.form['cost']
        item_reorder_level = request.form['reorder_level']
        new_inventory= {}

        new_item_id = inventory_list[len(inventory_list) - 1]['id'] + 1

        new_inventory['id'] = new_item_id
        new_inventory['sku'] = item_sku
        new_inventory['name'] = item_name
        new_inventory['description'] = item_description
        new_inventory['date'] = item_date
        new_inventory['quantity'] = item_quantity
        new_inventory['cost'] = item_cost
        new_inventory['reorder_level'] = item_reorder_level

        inventory_list.append(new_inventory)

        #write updated list to file

        df = pd.DataFrame(inventory_list).set_index('id') 
        df.to_csv('inventories.csv')
        return redirect(url_for('get_inventories'))

#route to edit each inventory list
@app.route('/inventories/<id>', methods=["GET", "PUT", "POST"])
def edit_item(id):
    #1. read the list of items from the csv file
    inventory_list = fetch_inventory_list()
    #2. find the item that matches the given id
    selected_item = None
    for item in inventory_list:
        if item['id'] == int(id):
            selected_item = item
            break
    #if it is a GET request, show the form with the data filled out in the form fields
    if request.method == 'GET':
        #return the edit-item template
        return render_template('edit-item.html', item=selected_item)
    
    else:
        data = {
            'id': item['id'],
            'sku': request.form['sku'],
            'name': request.form['name'],
            'description': request.form['description'],
            'date': request.form['date'],
            'quantity': request.form['quantity'],
            'cost': request.form['cost'],
            'reorder_level': request.form['reorder_level'],
        }
        #update items list by replacing existing item with the updated one
        #again, search for the one with matching id
        update_inventory(inventory_list, data)
        #write the changes to the file
        df = pd.DataFrame(inventory_list).set_index('id')
        df.to_csv('inventories.csv')
        return redirect(url_for('get_inventories'))

@app.route('/inventories/<id>/delete', methods=['POST','DELETE'])
def delete_item(id):
    delete_item(request.form['delete'])
    return redirect(url_for('get_inventories'))


def fetch_inventory_list():
    inventories = pd.read_csv('inventories.csv')
    return inventories.to_dict('records')

def update_inventory(inventory_list, new_item):
    for idx in range(len(inventory_list)):
        if new_item['id'] == inventory_list[idx]['id']:
            inventory_list[idx] = new_item
            break

def delete_item(id):
    inventory_list = fetch_inventory_list()
    new_list = [item for item in inventory_list if not (item['id'] == int(id)) ]
    df = pd.DataFrame(new_list).set_index('id')
    df.to_csv('inventories.csv')


if __name__ == '__main__':
    app.run(debug=True)