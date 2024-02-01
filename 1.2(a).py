#importing Modules 
import difflib
import json
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox  
import re
from datetime import datetime
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import timeit
from tkinter import simpledialog
from tkinter.filedialog import askopenfilename
from tkinter.simpledialog import askstring
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from matplotlib import colors
import threading

#class for handling product
class Product:
    product_id_counter = 1

    def __init__(self, name, quantity = 0, specification="", last_ordered =None):
        self.product_id = Product.product_id_counter
        Product.product_id_counter  = 1
        self.name = name
        self.quantity = quantity
        self.specification = specification
        self.last_ordered = last_ordered

    #for Order
    def order(self, quantity):
        if self.quantity >= quantity:
            self.quantity -= quantity
            self.last_ordered = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.replish()
            self.quantity -= quantity

    def copy(self):
        return Product (self.name, self.quantity, self.specification, self.last_ordered)

    def replenish(self):
        print(f"Replenishing {self.name}.")
        # ensure that the total quantity does not exceed more than 5
        self.quantity = min(self.quantity + 5, 5)            

#applying Linklist data structure for product

class Node:
    def __init__(self, product):
        self.product = product
        self.next = None

class ProductList:
    product_file = "product_file.txt"

    def __init__(self):
        #Head of linklist 
        self.head = None

    #Linklist datatstructure for adding product
    def add_product(self, product):
        new_node = Node(product)
        new_node.next = self.head
        self.head = new_node

    #for removing product
    def remove_product(self, product_id, product_name):
        current = self.head
        previous = None

        while current:
            if current.product.product_id == product_id and current.product.name == product_name:
                if previous:
                    previous.next = current.next
                else:
                    self.head = current.next

                self.log_product_update(product_name, current.product.quantity)
                return

            previous = current
            current = current.next

    #for updating the details for product in file
    def log_product_update(self, product):
        with open(ProductList.product_file, "a") as log_file:
            log_file.write(
                f"Product ID: {product.product_id}, "
                f"Name: {product.name}, "
                f"Quantity: {product.quantity}, "
                f"Last Updated: {datetime.now()}\n"
            )     

    #for searching product in warehouse 
    def search_product(self, search_id=None, search_name=None):
        current = self.head
        while current:
            product = current.product
            if (search_id and str(product.product_id) == search_id) or (
                search_name and product.name == search_name
            ):
                return product
            current = current.next

        return None                           

    #for displaying product in warehouse 
    def display_products(self):
        products_info = ""
        current = self.head
        while current:
            product = current.product
            products_info += (
                f"Product ID: {product.product_id}, "
                f"Name: {product.name}, "
                f"Quantity: {product.quantity}\n"
            )
            current = current.next

        return products_info
    
#product Class
class Product:
    PRODUCT_ID_COUNTER = 1

    def __init__(self, name, quantity=0, specification="", last_ordered=None):
        self.product_id = Product.PRODUCT_ID_COUNTER
        Product.PRODUCT_ID_COUNTER += 1
        self.name = name
        self.quantity = quantity
        self.specification = specification
        self.last_ordered = last_ordered
        

    def order(self, quantity):
        if self.quantity >= quantity:
            self.quantity -= quantity
            self.last_ordered = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.replenish()
            self.quantity -= quantity

    def copy(self, quantity=None):
        if quantity is None:
            quantity = self.quantity
        return Product(self.name, quantity, self.specification, self.last_ordered)

    def replenish(self):
        print(f"Replenishing {self.name}.")
        self.quantity += 5
    
#Queue data structre for Order 
class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)
    
#for order handling in warehouse
class Order:
    order_file = "order_file.txt"
    order_id_counter =1

    def __init__(self):
        self.order_id = Order.order_id_counter
        Order.order_id_counter+=1
        #use Queue for Products entry in Orders 
        self.product_queue = Queue()
        self.status = "registered"
        self.time_accepted = None
        self.time_collected = None


    #for adding products in order with help of Queue data structures
    def add_product(self, product):
        self.product_queue.enqueue(product) 

    #if order is been colleceted 
    def mark_collected(self):
        self.status = "collected"
        self.time_collected = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_order_update()

    #set the status of order as regsitered when the order is been added 
    def set_status(self, status):
        self.status = status
        if status == "registered":
            self.time_accepted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    def log_order_update(self):
        with open(Order.order_file, "a") as log_file:
            log_file.write(f"Order ID: {self.order_id}, Status: {self.status}, "
                           f"Time Accepted: {self.time_accepted}, Time Collected: {self.time_collected}, "
                           f"Number of Products: {self.product_queue.size()}, "
                           f"Product IDs: {[product.product_id for product in self.product_queue.items]}, "
                           f"Last Updated: {datetime.now()}\n")        
           
    def __str__(self):
        order_details = f"Order ID: {self.order_id}, Status: {self.status}\n"
        for product in self.product_queue.items:
            order_details += f"Product: {product.name}, Quantity: {product.quantity}, Specification: {product.specification}, Last Ordered: {product.last_ordered}\n"
        return order_details
    
#warehouse class for handling the events happening in warehouse
class Warehouse:
    max_orders = 5

    def __init__(self, root):
        self.root = root
        self.root.title("Warehouse Management Application")
        self.root.configure(bg="#ADD8E6")  # Set light orange background

        self.products = []
        self.orders = []
        self.product_list = ProductList()  # Initialize product_list attribute

        self.order_counter = 0

        self.create_widgets()
        self.start_time = timeit.default_timer()

    def create_widgets(self):
        heading_label = tk.Label(self.root, text="Warehouse Management", font='Helvetica 16 bold', bg="#ADD8E6",fg="#000000")
        heading_label.grid(row=0, column=5, columnspan=2, pady=10)
        
        style = ttk.Style()
        style.configure("TButton", padding=(5, 5, 5, 5), font='Helvetica 10 bold', background="#000000",foreground="#000000")
        style.configure("TEntry", font='Helvetica 10', background="#FFFFFF")
        style.configure("TLabel", font='Helvetica 10 bold', background="#FFFFFF", foreground="#000000")

        tk.Label(self.root, text="PRODUCT ID:", font='Helvetica 10 bold', bg="#FFFFFF", fg="#000000").grid(row=2,column=3,pady=5, padx=10,sticky=tk.W)
        tk.Label(self.root, text="PRODUCT NAME:", font='Helvetica 10 bold', bg="#FFFFFF", fg="#000000").grid(row=3,column=3,pady=5, padx=10,sticky=tk.W)
        tk.Label(self.root, text="QUANTITY:", font='Helvetica 10 bold', bg="#FFFFFF", fg="#000000").grid(row=4,column=3,pady=5, padx=10,sticky=tk.W)
        tk.Label(self.root, text="SPECIFICATION:", font='Helvetica 10 bold', bg="#FFFFFF", fg="#000000").grid(row=5,column=3,pady=5,padx=10,sticky=tk.W)
        tk.Label(self.root, text="LAST ORDERED:", font='Helvetica 10 bold', bg="#FFFFFF", fg="#000000").grid(row=6,column=3, pady=5,padx=10,sticky=tk.W)
        tk.Label(self.root, text="ORDER ID:", font='Helvetica 10 bold', bg="#FFFFFF", fg="#000000").grid(row=13,column=3,pady=5, padx=10,sticky=tk.W)

        self.product_id_entry = tk.Entry(self.root, font='Helvetica 10', bg="#FFFFFF")
        self.product_name_entry = tk.Entry(self.root, font='Helvetica 10', bg="#FFFFFF")
        self.quantity_entry = tk.Entry(self.root, font='Helvetica 10', bg="#FFFFFF")
        self.specification_entry = tk.Entry(self.root, font='Helvetica 10', bg="#FFFFFF")
        self.last_ordered_entry = tk.Entry(self.root, font='Helvetica 10', bg="#FFFFFF")
        self.order_id_entry = tk.Entry(self.root, font='Helvetica 10', bg="#FFFFFF")

        self.product_id_entry.grid(row=2, column=4, pady=5, padx=10, sticky=tk.W)
        self.product_name_entry.grid(row=3, column=4, pady=5, padx=10, sticky=tk.W)
        self.quantity_entry.grid(row=4, column=4, pady=5, padx=10, sticky=tk.W)
        self.specification_entry.grid(row=5, column=4, pady=5, padx=10, sticky=tk.W)
        self.last_ordered_entry.grid(row=6, column=4, pady=5, padx=10, sticky=tk.W)
        self.order_id_entry.grid(row=13, column=4, pady=5, padx=10, sticky=tk.W)
        #for adding
        ttk.Button(self.root, text="ADD PRODUCT", command=self.adding_product).grid(row=7, column=2, pady=10)
        #for removing
        ttk.Button(self.root, text="REMOVE PRODUCT", command=self.removing_product).grid(row=7, column=4, pady=10)
        #for adding order
        ttk.Button(self.root, text="ADD ORDER", command=self.adding_order).grid(row=8, column=2, pady=10)
        #removing order
        ttk.Button(self.root, text="REMOVE ORDER", command=self.removing_order).grid(row=8, column=4, pady=10)
        #searching info
        ttk.Button(self.root, text="SEARCH PRODUCT", command=self.search_product).grid(row=9, column=2, pady=10)
        #product information
        ttk.Button(self.root, text="PRODUCT INFORMATION", command=self.product_information).grid(row=9, column=4, pady=10)
        #order informatiom
        ttk.Button(self.root, text="ORDER INFORMATION", command=self.order_information).grid(row=10, column=2, pady=10)
        #put order in queue
        ttk.Button(self.root, text="ORDER IN QUEUE BY ORDER ID", command=self.queue_by_order_identity).grid(row=10, column=4, pady=10)
        #mark colllected by order id
        ttk.Button(self.root, text="MARK COLLECTED BY ORDER ID", command=self.mark_collected_order_identity).grid(row=11, column=2, pady=10)
        #remove by order id
        ttk.Button(self.root, text="REMOVE ORDER BY ID", command=self.remove_order_by_identity).grid(row=11, column=4, pady=10)
        #checking similairty
        ttk.Button(self.root, text="Check Similarity", command=self.check_similarity).grid(row=12, column=2, pady=10)
        self.time_label = tk.Label(self.root, text="Elapsed Time: 0.00 seconds", font='Helvetica 10 bold', bg="#FFFFFF", fg="#000000")
        self.time_label.grid(row=13, column=5, columnspan=2, pady=10)
        ttk.Button(self.root, text="VIEW PRODUCT FILE", command=self.view_product_log_file).grid(row=7, column=7, columnspan=2, pady=10)
        ttk.Button(self.root, text="VIEW ORDER FILE", command=self.view_order_log_file).grid(row=13, column=7, columnspan=2, pady=10)
        ttk.Button(self.root, text="SHOPPING LIST", command=self.shopping_list_pdf).grid(row=9, column=6, pady=10)
        ttk.Button(self.root, text="GENERATE PDF REPORT", command=self.generate_pdf).grid(row=10, column=6, pady=10)
    
        #a small text box to display similarity
        self.similarity_text_box = tk.Text(self.root, height=3, width=30, font='Helvetica 10', wrap=tk.WORD,bg="#EFEFEF", fg="#000000")
        self.similarity_text_box.grid(row=12, column=4, pady=5, padx=10, sticky=tk.W)
        frame_product = tk.Frame(self.root, bg="#EFEFEF")
        frame_product.grid(row=2, column=8, rowspan=5, padx=10, pady=10, sticky=tk.NSEW)

        product_heading_label = tk.Label(frame_product, text="Product Information", font='Helvetica 12 bold',bg="#EFEFEF", fg="#000000")
        product_heading_label.pack()

        self.product_text_box = tk.Text(frame_product, height=15, width=25, font='Helvetica 10', wrap=tk.WORD,bg="#EFEFEF", fg="#000000")
        self.product_text_box.pack(side=tk.LEFT, expand=True)

        frame_order = tk.Frame(self.root, bg="#EFEFEF")
        frame_order.grid(row=8, column=8, rowspan=5, padx=10, pady=10, sticky=tk.NSEW)

        order_heading_label = tk.Label(frame_order, text="Order Information", font='Helvetica 12 bold',bg="#EFEFEF", fg="#000000")
        order_heading_label.pack()

        self.order_text_box = tk.Text(frame_order, height=15, width=30, font='Helvetica 10', wrap=tk.WORD,bg="#EFEFEF", fg="#000000")
        self.order_text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_order = tk.Scrollbar(frame_order, command=self.order_text_box.yview)
        scrollbar_order.pack(side=tk.RIGHT, fill=tk.Y)
        self.order_text_box.config(yscrollcommand=scrollbar_order.set)


        self.specification_entry.bind("<KeyRelease>", self.check_similarity)


    #function for adding product in warehouse
    def adding_product(self):
        product_name = self.product_name_entry.get()
        quantity = int(self.quantity_entry.get())
        last_ordered = self.last_ordered_entry.get()
        specification = self.specification_entry.get()

        # Check if the quantity exceeds the limit
        if quantity > 5:
            messagebox.showerror("Error", "Quantity cannot exceed 5. Please enter a quantity of 5 or less.")
            return

        product = Product(product_name, quantity, specification, last_ordered)
        order_product = product.copy()

        self.product_list.add_product(order_product)
        self.update_elapsed_time_label()

        # Run the GUI-related update in a separate thread
        gui_thread = threading.Thread(target=self.update_product_text_area)
        gui_thread.start()

        messagebox.showinfo("Success", f"Product {product_name} added successfully.")
        self.product_list.log_product_update(product)

        

      

    #function to remove the product for warehouse
    def removing_product(self):
        # Prompt the user for product ID or name
        product_id_or_name = simpledialog.askstring("Remove Product", "Enter product ID or name:")
        if product_id_or_name is None:
            return  # User canceled the removal

        # Prompt the user for quantity to remove
        quantity_to_remove = simpledialog.askinteger("Remove Product", f"Enter the quantity to remove for product {product_id_or_name}:")
        if quantity_to_remove is None:
            return  # User canceled the removal

        # Check if the entered quantity is valid
        if quantity_to_remove <= 0:
            messagebox.showerror("Error", "Invalid quantity. Please enter a valid positive integer.")
            return

        # Search for the product in the linked list
        current = self.product_list.head
        previous = None

        while current:
            current_product = current.product

            if (str(current_product.product_id) == product_id_or_name) or (current_product.name == product_id_or_name):
                # Check if the entered quantity is valid
                if quantity_to_remove > current_product.quantity:
                    messagebox.showerror("Error", f"Invalid quantity. The available quantity for product {current_product.name} is {current_product.quantity}.")
                    return

                # Remove the specified quantity from the product
                current_product.quantity -= quantity_to_remove

                # If the quantity becomes 0 or negative, remove the entire product
                if current_product.quantity <= 0:
                    if previous:
                        previous.next = current.next
                    else:
                        self.product_list.head = current.next

                # Update the displayed products
                self.update_product_text_area()

                messagebox.showinfo("Success", f"{quantity_to_remove} units of product {current_product.name} removed successfully.")
                self.product_list.log_product_update(current_product.name, quantity_to_remove)
                return

            previous = current
            current = current.next

        messagebox.showerror("Error", f"No product found with ID or name {product_id_or_name}.")
  


    #add Order in warehouse function
    def adding_order(self):
    # Check if the maximum order limit is reached
        if self.order_counter >= Warehouse.max_orders:
            messagebox.showinfo("Order Limit", "Order limit reached. You cannot create more orders.")
            return

        if not self.product_list.head:
            print("No products available to create an order.")
            messagebox.showerror("Error", "No products available to create an order.")
            return  # Return here to avoid incrementing order_counter

        # Create a new order instance for each order
        new_order = Order()

        while True:
            # Prompt the user for product ID or name
            product_id_or_name = simpledialog.askstring("Add Order", "Enter product ID or name (or cancel to finish):")
            if product_id_or_name is None:
                break  # User canceled the order

            # Prompt the user for quantity to order
            ordered_quantity = simpledialog.askinteger("Add Order", f"Enter quantity to order for product {product_id_or_name} (Available: 5):",
                                                        minvalue=1, maxvalue=5)

            if ordered_quantity is None:
                break  # User canceled the order for this product

            product = self.product_list.search_product(search_id=product_id_or_name, search_name=product_id_or_name)
            if product:
                if 0 < ordered_quantity <= product.quantity:
                    order_product = product.copy(quantity=ordered_quantity)
                    print(f"Product ID: {order_product.product_id}, Name: {order_product.name}, Quantity: {order_product.quantity}")
                    new_order.add_product(order_product)

                    # Decrement the quantity of the ordered product in the warehouse
                    product.quantity -= ordered_quantity

                    # Update the displayed products
                    self.update_product_text_area()

                    # Break out of the loop after successfully adding the product
                    break
                else:
                    messagebox.showerror("Error", "Invalid quantity. Please enter a valid quantity.")
            else:
                messagebox.showerror("Error", f"No product found with ID or name {product_id_or_name}.")

        if not new_order.product_queue.items:
            print("No products available to create an order.")
            messagebox.showerror("Error", "No products available to create an order.")
            return

        new_order.set_status("registered")  # Set the initial status

        # Add the new order instance to the list
        self.orders.append(new_order)

        # Clear the text box before updating orders text area
        self.order_text_box.delete(1.0, tk.END)

        # Display all orders, including collected orders
        for order in self.orders:
            self.display_order(order)

        if self.order_counter >= Warehouse.max_orders:
            oldest_order = min(self.orders, key=lambda x: x.time_accepted)
            self.orders.remove(oldest_order)

        # Display the order ID in the GUI
        messagebox.showinfo("Order Added", f"Order {new_order.order_id} added successfully. Status: {new_order.status}")
        new_order.log_order_update()

        # Update the collected orders
        self.remove_collected_orders()

        # Increment order_counter only if the order was successfully created
        self.order_counter = len([order for order in self.orders if order.status != "collected"])

        # Update the product information text box
        self.display_products()



      

    def removing_order(self):
        # Get the order ID from the user
        product_id_or_name = simpledialog.askstring("Input", "Enter Order ID or Product ID/Name to remove:")

        # Check if the user canceled the input
        if product_id_or_name is None:
            return

        # Create a list to store orders to be removed
        orders_to_remove = []

        for order in self.orders:
            # Check if the order ID matches
            if str(order.order_id) == product_id_or_name:
                orders_to_remove.append(order)
                continue

            # Check if the product ID or name matches within the order
            for product in order.product_queue.items:
                if product.product_id == product_id_or_name or product.name == product_id_or_name:
                    orders_to_remove.append(order)
                    break

        # Remove the identified orders
        for order in orders_to_remove:
            if order.status == "collected":
                # Decrement order counter for collected orders
                self.order_counter -= 1
                messagebox.showinfo("Info", "Collected order will be automatically removed.")
            else:
                # Return products from the removed order back to the warehouse
                for product in order.product_queue.items:
                    product.replenish()  # Assuming you have a replenish method in your Product class
                    self.products.append(product.copy())

                # Remove the order from the list
                self.orders.remove(order)

                # Decrement order counter for non-collected orders
                self.order_counter -= 1

                # Update text areas
                self.update_orders_text_area()
                self.update_product_text_area()  # Update products text area

                # Display success message
                messagebox.showinfo("Success", f"Order {order.order_id} removed successfully. Quantities returned to warehouse.")

        # Display an error message if no orders were found
        if not orders_to_remove:
            messagebox.showerror("Error", f"No order found with Order ID or Product ID/Name {product_id_or_name}.")


        #to display product information function
    def product_information(self): 
            # Ask the user to enter product name or ID using simpledialog
            product_id_or_name = simpledialog.askstring("Product Information", "Enter product ID or name:")

            if product_id_or_name is not None:
                # Search for the product in the linked list
                current = self.product_list.head
                while current:
                    product = current.product
                    if str(product.product_id) == product_id_or_name or product.name == product_id_or_name:
                        # Display product information in a message box
                        info = (
                            f"Product ID: {product.product_id}\n"
                            f"Product Name: {product.name}\n"
                            f"Available Quantity: {product.quantity}\n"
                            f"Specification: {product.specification}\n"
                            f"Last Ordered: {product.last_ordered}\n"
                        )
                        messagebox.showinfo("Product Information", info)
                        return

                    current = current.next

                # Display an error message if no product is found
                messagebox.showinfo("Product Information", f"No product with ID or name {product_id_or_name}.")        


    #updating order text area
    def update_orders_text_area(self):
        self.order_text_box.delete(1.0, tk.END)
        #display the order that is not been colleceetd
        for order in self.orders:
            if order.status != "collected":
                self.display_order(order)

    #things to display products
    def display_products(self):
        # Clear the text box before updating product information
        self.product_info_text_box.delete(1.0, tk.END)

        # Display product information, including quantity
        self.product_info_text_box.insert(tk.END, "Product Information:\n\n")
        current_product = self.product_list.head
        while current_product:
            product_str = f"ID: {current_product.product_id}, Name: {current_product.name}, Quantity: {current_product.quantity}\n"
            self.product_info_text_box.insert(tk.END, product_str)
            current_product = current_product.next

        # Scroll to the top after updating
        self.product_info_text_box.yview(tk.END)

    def display_products(self):
        products_info = self.product_list.display_products()
        self.order_text_box.insert(tk.END, products_info)    

    def update_product_text_area(self):
        self.product_text_box.delete(1.0, tk.END)
        self.display_products()              


    def queue_by_order_identity(self):
        # Ask the user for the order ID using simpledialog
        order_id = simpledialog.askstring("Change Order Status", "Enter Order ID:")

        if order_id is not None:
            for order in self.orders:
                if str(order.order_id) == order_id:
                    # Change the status of the order to "in the collection queue"
                    order.set_status("in the collection queue")
                    self.update_orders_text_area()
                    messagebox.showinfo("Success", f"Order {order_id} is now in the collection queue.")
                    return

            # Display an error message if no order is found with the entered ID
            messagebox.showerror("Error", f"No order found with ID {order_id}.")

    def mark_collected_order_identity(self):
        order_id = simpledialog.askstring("Mark Collected Order", "Enter Order ID to put in Collection:")

        for order in self.orders:
            if str(order.order_id) == order_id:
                order.set_status("Collected")
                order.mark_collected()
                self.remove_collected_orders()
                messagebox.showinfo("Success", f"Order {order_id} is now collected.")
                break
        else:
            messagebox.showerror("Error", f"No order found with ID {order_id}.")

    def order_information(self):
        # Ask the user for the order ID using simpledialog
        order_info_input = simpledialog.askstring("Order Information", "Enter Order ID:")

        # Check if the input is a number (order ID)
        if order_info_input.isdigit():
            # Search by order ID
            order_info = next((order for order in self.orders if str(order.order_id) == order_info_input), None)
        else:
            order_info = None

        if order_info:
            # Display order details in a message box
            order_details = (
                f"Order ID: {order_info.order_id}\n"
                f"Status: {order_info.status}\n"
                f"Time Accepted: {order_info.time_accepted}\n"
                f"Time Collected: {order_info.time_collected}\n"
                f"Number of Products: {order_info.product_queue.size()}\n"  # Use product_queue.size() instead of len(order_info.products)
                f"Product IDs: {[product.product_id for product in order_info.product_queue.items]}\n"
            )
            messagebox.showinfo("Order Information", order_details)
        else:
            messagebox.showerror("Error", "Order not found.")

    def remove_collected_orders(self):
        # Remove collected orders from the list
        self.orders = [order for order in self.orders if order.status != "collected"]
        
        # Update the displayed orders after removing collected orders
        self.update_orders_text_area()

        # Decrement order counter only for non-collected orders
        self.order_counter = len([order for order in self.orders if order.status != "collected"])

        

    def remove_order_by_identity(self):
        order_id = self.order_id_entry.get()

        for order in self.orders:
            if str(order.order_id) == order_id:
                if order.status == "collected":
                    self.order_counter -= 1  # Decrement order counter for collected orders
                    messagebox.showinfo("Info", "Collected order will be automatically removed.")
                else:
                    self.orders.remove(order)
                    self.order_counter -= 1  # Decrement order counter for non-collected orders
                    self.update_orders_text_area()
                    messagebox.showinfo("Success", f"Order {order_id} removed successfully.")
                break
        else:
            messagebox.showerror("Error", f"No order found with ID {order_id}.")

    def display_order(self, order):
        self.order_text_box.insert(tk.END, str(order) + "\n\n")
    

    def show_time(self):
        if self.start_time is None:
            self.start_time = timeit.default_timer()
            self.update_elapsed_time_label()

    def update_elapsed_time_label(self):
        if self.start_time is not None:
            elapsed_time = timeit.default_timer() - self.start_time
            self.elapsed_time_label.config(text=f"Elapsed Time: {elapsed_time:.2f} seconds")
      
    def search_product(self):
        search_id = self.product_id_entry.get()
        search_name = self.product_name_entry.get()

        # Search for the product in the linked list
        result_product = self.product_list.search_product(search_id=search_id, search_name=search_name)

        if result_product:
            if result_product.quantity == 0:
                messagebox.showinfo("Product Status", "Out of stock")
            else:
                messagebox.showinfo("Product Status", f"Product {result_product.name} is in stock.")
        else:
            messagebox.showinfo("Product Status", "No product with this name or ID.")

    def check_similarity(self):
        # Ask the user for the product name or ID using simpledialog
        product_identifier = simpledialog.askstring("Check Similarity", "Enter Product Name or ID:")

        if product_identifier:
            current_specification = self.specification_entry.get().lower()
            similar_products = []

            for product in self.products:
                product_specification = product.specification.lower()
                if product.name.lower() != product_identifier.lower():
                    similarity_ratio = difflib.SequenceMatcher(None, current_specification, product_specification).ratio()
                    # Consider a match if the similarity ratio is above a certain threshold (e.g., 70%)
                    if similarity_ratio > 0.7:
                        similar_products.append((product, similarity_ratio))

            # Clear previous content in the text box
            self.similarity_text_box.delete(1.0, tk.END)

            # Display the result in the similarity_text_box
            if similar_products:
                self.similarity_text_box.insert(tk.END, "Similar Products Found:\n")
                for product, similarity_ratio in similar_products:
                    self.similarity_text_box.insert(tk.END, f"{product.name} (ID: {product.product_id}) - Similarity: {similarity_ratio*100:.2f}%\n")
            else:
                self.similarity_text_box.insert(tk.END, "No similar products found.\n")
    def update_product_text_area(self):
        self.product_text_box.delete(1.0, tk.END)

        # Display the updated product information
        self.product_list.display_products()
        products_info = self.product_list.display_products()
        self.product_text_box.insert(tk.END, products_info)            

    def update_elapsed_time_label(self):
        if self.start_time is not None:
            elapsed_time = timeit.default_timer() - self.start_time
            print(f"Elapsed Time: {elapsed_time:.2f} seconds")

    def view_product_log_file(self):
        try:
            # Open the log file using the default text editor
            os.system(f"notepad.exe {ProductList.product_file}")
        except Exception as e:
            print(f"Error opening log file: {e}")  

    def view_order_log_file(self):
        try:
            # Open the order log file using the default text editor
            os.system(f"notepad.exe {Order.order_file}")
        except Exception as e:
            print(f"Error opening order log file: {e}") 

    # to generate the pdf for the products
    def generate_pdf(self):
        try:
            with open(ProductList.product_file, "r") as log_file:
                content = log_file.read()

            # create pdf
            pdf_file = "PDF Report.pdf"
            pdf_canvas = SimpleDocTemplate(pdf_file, pagesize=letter)

            # extract product info
            product_info = [line.strip() for line in content.split("\n") if line.strip()]

            # define table data
            table_data = [['Product ID', 'Product Name', 'Quantity', 'Last Updated']]

            for info in product_info:
                product_match = re.search(
                    r"Product ID: (\d+), Name: (.+), Quantity: (\d+), Last Updated: (.+)", info
                )
                if product_match:
                    product_id = int(product_match.group(1))
                    product_name = product_match.group(2)
                    quantity = int(product_match.group(3))
                    last_updated = product_match.group(4)
                    if quantity >0:
                        table_data.append([product_id, product_name, quantity, last_updated])

            # create table
            table = Table(table_data)
            style = TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, 0), (0.7, 0.7, 0.7)),  # RGB tuple for light gray
                    ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),  # RGB tuple for black
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 0), (-1, 0), (1, 1, 1)),  # RGB tuple for white
                    ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),  # RGB tuple for black
                    ('TEXTCOLOR', (0, 0), (-1, -1), (0, 0, 0)),  # RGB tuple for black
                ]
            )

            table.setStyle(style)
            pdf_canvas.build([table])
            messagebox.showinfo("Report Generated", f"PDF Report {pdf_file} has been Generated")

        except FileNotFoundError:
            messagebox.showinfo("File Not Found", "Product log File Not Found")
 

    def shopping_list_pdf(product_file):
        try:
            with open(ProductList.product_file, "r") as log_file:
                content = log_file.read()

            # create a pdf report
            pdf_file = "SHOPPING_LIST.pdf"
            pdf_canvas = SimpleDocTemplate(pdf_file, pagesize=letter)

            # extract product information
            product_info = [line.strip() for line in content.split("\n") if line.strip()]

            # define the data for the table
            table_data = [['Product ID', 'Product Name', 'Quantity']]
            for info in product_info:
                product_match = re.search(r"Product ID: (\d+), Name: (.+), Quantity: (\d+), Last Updated: (.+)", info)
                if product_match:
                    product_id = int(product_match.group(1))
                    product_name = product_match.group(2)
                    quantity = int(product_match.group(3))

                    if quantity == 0:
                        table_data.append([product_id, product_name, quantity])

            # Check if there are products with zero quantity for the shopping list
            if len(table_data) > 1:
                # create a table and set its style
                table = Table(table_data)
                style = TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, 0), (0.7, 0.7, 0.7)),  # RGB tuple for light gray
                    ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),  # RGB tuple for black
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 0), (-1, 0), (1, 1, 1)),  # RGB tuple for white
                    ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),  # RGB tuple for black
                    ('TEXTCOLOR', (0, 0), (-1, -1), (0, 0, 0)),  # RGB tuple for black
                ]
            )

                table.setStyle(style)
                pdf_canvas.build([table])

                messagebox.showinfo("Report Generated", f"PDF report '{pdf_file}' generated successfully")
            else:
                messagebox.showinfo("No Products", "No products with zero quantity found for the shopping list.")
        except FileNotFoundError:
            messagebox.showinfo("File not Found", "Product log file not found")        

    def update_product_text_file(self):
    # Rewrite the product text file with updated quantities
        with open(Product.log_file_product, "w") as log_file:
            for product in self.products:
                log_file.write(
                    f"{product.name} ({product.product_id}): Quantity = {product.quantity}, "
                    f"Last Ordered = {product.last_ordered}, Last Updated = {datetime.now()}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = Warehouse(root)
    root.mainloop()                  