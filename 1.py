#importing Different modules
import re
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import timeit
from tkinter import simpledialog
import difflib
from matplotlib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

#class for handling product in the warehouse 
class Product:
    product_file = "product_file"
    product_id_counter = 1

    def __init__(self, name, quantity=0, specification="", last_ordered =None):
        #attributes for warehouse for product entry
        self.product_id = self.product_id_counter
        Product.product_id_counter +=1
        self.specification = specification
        self.name = name
        self.quantity =quantity
        self.last_ordered = last_ordered

        #to manage the order and retain
    def order(self, quantity):
        if self.quantity >= quantity:
            self.quantity -=quantity
            self.last_ordered = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.replenish()
            self.quantity -= quantity

    def replenish(self):
        print(f"replenishing {self.name}")
        self.quantity +=5
        self.product_update()

    def copy(self):
        return Product(self.name, self.quantity, self.specification, self.last_ordered) 

    def product_update(self):
        with open(Product.product_file, "a") as log_file:
            log_file.write(
                f"{self.name} ({self.product_id}): Quantity={self.quantity}, Last Updated={datetime.now()}\n"
            )
    def product_update(self):
        with open(Product.product_file, "a") as log_file:
            log_file.write(
                f"{self.name} ({self.product_id}): Quantity={self.quantity}, Last Updated={datetime.now()}\n"
            )

#class for handling order in the warehouse 
class Order:
    log_file_order = "Order_file"
    order_id_counter = 1

    def __init__(self):
        self.order_id = Order.order_id_counter
        Order.order_id_counter +=1
        self.products = [] #for storing the products data in order
        self.time_accepted = None
        self.status = "registered" #for when the order is been registered
        self.time_collected = None

    # appending or adding all products in the order
    def adding_product_warehouse(self, product):
        self.products.append(product)

    #if order is being there with product the status should be registered
    def set_status(self, status):
        self.status = status
        if status == "Registered":
            self.time_accepted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #if the order is been collected
    def mark_collected(self):
        self.status = "Collected"
        self.time_collected = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.order_update()

    #function to add the data of the order in the file
    def order_update(self):
        with open(Order.log_file_order, "a") as log_file:
            log_file.write(
                f"Order ID :{self.order_id}, Status: {self.status},"
                f"Accepted time:{self.time_accepted}, Time Collected: {self.time_collected},"
                f"No of Products:{len(self.products)}, Products ID: {[product.product_id for product in self.products]},"
                f"Last Updated: {datetime.now()}\n")  

    def __str__(self):
        order_details = f"Order Id: {self.order_id}, status:{self.status}\n"
        for product in self.products:
            order_details += f"Products: {product.name}, Quantity: {product.quantity}, specification: {product.specification}, Last Ordered: {self.last_ordered}\n"
            return order_details
        
#Creating wraehouse class for handling different operation in warehouse
class warehouse:
    max_orders = 5

    def __init__(self, root):
        self.root = root
        self.root.title("WAREHOUSE MANAGEMENT")
        self.root.configure(bg="#C1FFC1")
        self.products = []
        self.orders = []
        self.order_counter = 0
        self.start_time =  timeit.default_timer()
        self.create_widgets()                 

    #creating Different Widgets for warehouse 
    def create_widgets(self):
        heading_label = tk.Label(self.root, text="Warehouse Management", font='Helvetica 16 bold', bg="#C1FFC1",fg="#000000")
        heading_label.grid(row=0, column=5, columnspan=2, pady=10)

        style = ttk.Style()
        style.configure("TButton", padding=(5, 5, 5, 5), font='Helvetica 10 bold', background="#000000",foreground="#000000")
        style.configure("TEntry", font='Helvetica 10', background="#FFFFFF")
        style.configure("TLabel", font='Helvetica 10 bold', background="#FFFFFF", foreground="#000000")

        #Lables for Entering product details
        tk.Label(self.root, text="PRODUCT ID:", font='Helvetica 10 bold', bg="#FFFFFF", fg="#000000").grid(row=2,column=3,pady=5, padx=10,sticky=tk.W)
        tk.Label(self.root, text="PRODUCT NAME:", font='Helvetica 10 bold', bg="#FFFFFF", fg="#000000").grid(row=3,column=3,pady=5, padx=10,sticky=tk.W)
        tk.Label(self.root, text="QUANTITY:", font='Helvetica 10 bold', bg="#FFFFFF", fg="#000000").grid(row=4,column=3,pady=5, padx=10,sticky=tk.W)
        tk.Label(self.root, text="SPECIFICATION:", font='Helvetica 10 bold', bg="#FFFFFF", fg="#000000").grid(row=5,column=3,pady=5,padx=10,sticky=tk.W)
        tk.Label(self.root, text="LAST ORDERED:", font='Helvetica 10 bold', bg="#FFFFFF", fg="#000000").grid(row=6,column=3, pady=5,padx=10,sticky=tk.W)
        tk.Label(self.root, text="ORDER ID:", font='Helvetica 10 bold', bg="#FFFFFF", fg="#000000").grid(row=13,column=3,pady=5, padx=10,sticky=tk.W)

        #Styling the Lables
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

        #Creating the buttons for the warehouse
        #for adding
        ttk.Button(self.root, text="ADD PRODUCT", command=self.adding_product_warehouse).grid(row=7, column=2, pady=10)
        #for removing
        ttk.Button(self.root, text="REMOVE PRODUCT", command=self.removing_product_warehouse).grid(row=7, column=4, pady=10)
        #for adding order
        ttk.Button(self.root, text="ADD ORDER", command=self.adding_order_warehouse).grid(row=8, column=2, pady=10)
        #for removing order
        ttk.Button(self.root, text="REMOVE ORDER", command=self.removing_order_warehouse).grid(row=8, column=4, pady=10)
        #for searching order
        ttk.Button(self.root, text="SEARCH PRODUCT", command=self.search_product).grid(row=9, column=2, pady=10)
        #for product information
        ttk.Button(self.root, text="PRODUCT INFORMATION", command=self.product_information_warehouse).grid(row=9, column=4, pady=10)
        #for order information
        ttk.Button(self.root, text="ORDER INFORMATION", command=self.order_information_warehouse).grid(row=10, column=2, pady=10)
        #to put order in queue
        ttk.Button(self.root, text="ORDER IN QUEUE BY ORDER ID", command=self.queue_by_order_id).grid(row=10, column=4, pady=10)
        #to mark order as collecetd
        ttk.Button(self.root, text="MARK COLLECTED BY ORDER ID", command=self.mark_collected_order_id).grid(row=11, column=2, pady=10)
        #if any glitch is there we cna remove order by id or mark collected
        ttk.Button(self.root, text="REMOVE ORDER BY ID", command=self.removing_order_warehouse_by_id).grid(row=11, column=4, pady=10)
        #to check the similarity of order
        ttk.Button(self.root, text="Check Similarity", command=self.checking_similarity_warehouse).grid(row=12, column=2, pady=10)
        #to generate pdf 
        ttk.Button(self.root, text="Generate PDF Report", command=self.generate_pdf).grid(row=12, column=6, pady=10)
        self.time_label = tk.Label(self.root, text="Elapsed Time: 0.00 seconds", font='Helvetica 10 bold', bg="#FFFFFF", fg="#000000")
        self.time_label.grid(row=13, column=5, columnspan=2, pady=10)
        #to view log_file of product
        ttk.Button(self.root, text="View Product File", command=self.view_product_log_file).grid(row=7, column=7, columnspan=2, pady=10)
        #to view order log file
        ttk.Button(self.root, text="View Order Log File", command=self.view_order_log_file).grid(row=13, column=7, columnspan=2, pady=10)
        #to generate shopping list if product are zero
        ttk.Button(self.root, text="Generate Shopping List", command=self.generate_shopping_list_pdf).grid(row=11, column=6, pady=10)
        #a small text box to display similarity
        self.similarity_text_box = tk.Text(self.root, height=3, width=30, font='Helvetica 10', wrap=tk.WORD,bg="#EFEFEF", fg="#000000")
        self.similarity_text_box.grid(row=12, column=4, pady=5, padx=10, sticky=tk.W)
        #frame for product to display the product details
        frame_product = tk.Frame(self.root, bg="#EFEFEF")
        frame_product.grid(row=2, column=8, rowspan=5, padx=10, pady=10, sticky=tk.NSEW)

        product_heading_label = tk.Label(frame_product, text="Product Information", font='Helvetica 12 bold',bg="#EFEFEF", fg="#000000")
        product_heading_label.pack()

        self.product_text_box = tk.Text(frame_product, height=15, width=20, font='Helvetica 10', wrap=tk.WORD,bg="#EFEFEF", fg="#000000")
        self.product_text_box.pack(side=tk.LEFT, expand=True)

        #Frame for Showing the data of the orders
        frame_order = tk.Frame(self.root, bg="#EFEFEF")
        frame_order.grid(row=8, column=8, rowspan=5, padx=10, pady=10, sticky=tk.NSEW)

        order_heading_label = tk.Label(frame_order, text="Order Information", font='Helvetica 12 bold',bg="#EFEFEF", fg="#000000")
        order_heading_label.pack()

        self.order_text_box = tk.Text(frame_order, height=15, width=30, font='Helvetica 10', wrap=tk.WORD,bg="#EFEFEF", fg="#000000")
        self.order_text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_order = tk.Scrollbar(frame_order, command=self.order_text_box.yview)
        scrollbar_order.pack(side=tk.RIGHT, fill=tk.Y)
        self.order_text_box.config(yscrollcommand=scrollbar_order.set)


        self.update_time_label(self.start_time)

    def update_time_label(self, start_time):
        elapsed_time = timeit.default_timer() - start_time
        self.time_label.config(text=f"Elapsed Time: {elapsed_time:.2f} seconds")
        self.root.after(1000, lambda: self.update_time_label(start_time))  # Schedule the next update after 1000 milliseconds (1 second)
    
    #Function for Adding the product in the warehouse
    def adding_product_warehouse(self):
        product_id = self.product_id_entry.get()  # for Product id
        product_name = self.product_name_entry.get()  # for entering the product name
        quantity = int(self.quantity_entry.get())  # for quantity of the product
        last_ordered = self.last_ordered_entry.get()  # for specification of the product
        specification = self.specification_entry.get()  # for giving the specification of the product

        existing_product = next((product for product in self.products if product.name == product_name), None)

        if existing_product:
            updated_quantity = min(int(existing_product.quantity) + quantity, 5)
            if updated_quantity > 5:
                messagebox.showwarning("Quantity Limit", "You can only add up to 5 quantities for a product.")
                return
            existing_product.quantity = str(updated_quantity)
            existing_product.last_ordered = last_ordered
            existing_product.product_update()
            self.display_product(existing_product)
            elapsed_time = timeit.default_timer() - self.start_time
            self.time_label.config(text=f"Elapsed Time: {elapsed_time:.2f} seconds")
            messagebox.showinfo(f"Quantity has been updated for product {product_name}.")
        else:
            if quantity > 5:
                messagebox.showwarning("Quantity Limit", "You can only add up to 5 quantities for a product.")
                return
            new_product = Product(product_name, min(quantity, 5), specification, last_ordered)
            new_product.product_id = product_id
            self.products.append(new_product)  # to add new product by append method
            self.display_product(new_product)
            new_product.product_update()
            elapsed_time = timeit.default_timer() - self.start_time
            self.time_label.config(text=f"Elapsed Time: {elapsed_time:.2f} seconds")
            messagebox.showinfo("Success", f"{product_name} {quantity} has been added to the warehouse.")
    #for removing the product from the warehouse
    def removing_product_warehouse(self):
        #prompt user to enter the product to remove by name or id
        product_identifier = simpledialog.askstring("Input", "Enter Product name or ID")

        #if product is not avalibale in the warehouse then it will shopw error
        if not product_identifier:
            messagebox.showerror("Error", "Please enter a valid product name or ID")
            return
        #prompt the user to remove the quantity of the product
        quantity_to_remove_str = simpledialog.askstring("Input", f"Please enter the quantity to remove for {product_identifier}:")

        #if quantity is not integer
        if not quantity_to_remove_str.isdigit():
            messagebox.showerror("Error", "please enter a valid quantity to remove from warehouse")

        quantity_to_remove = int(quantity_to_remove_str)

        for product in self.products:
            if product.name.lower() == product_identifier.lower() or str(product.product_id) == product_identifier:
                if product.quantity ==0:
                    messagebox.showerror("Product is out of stock")
                elif quantity_to_remove > product.quantity:
                    messagebox.showerror("Cannot remove more quantity then avaliable")
                else:
                    product.quantity -= quantity_to_remove

        #check if the product is out of stock
            if product.quantity ==0:
                self.products.remove(product)

            self.display_products() #to update the product in the frame 

            #update the log file
            with open (Product.product_file, "a") as log_file:
                log_file.write(
                    f"{product.name} ({product.product_id}): Quantity= {product.quantity}, Last Updated={datetime.now()}\n")

            #Show a message that the quantity has been removed successfully
            messagebox.showinfo("Success",f"{quantity_to_remove} removed from the {product_identifier}")
            return

        #if the product is not found show and error message
        messagebox.showerror("Success",f"'{product_identifier}' is not been found in warehouse")   

    #Function to handle to add order 
    def adding_order_warehouse(self):
        if len(self.orders) >= warehouse.max_orders:
            messagebox.showinfo("Order Limit Reached", "You cannot create more orders.")
            return

        if not self.products:
            messagebox.showerror("No Products Available", "There are no products available to create an order.")
            return

        product_id = simpledialog.askstring("Product ID", "Enter a Product ID to create an order:")
        quantity = simpledialog.askinteger("Quantity", "Enter a Quantity for the order:")

        product_to_add = next((product for product in self.products if str(product.product_id) == product_id), None)

        if product_to_add:
            if int(product_to_add.quantity) >= quantity:
                order_product_quantity = quantity
            else:
                order_product_quantity = int(product_to_add.quantity)

            order_product = product_to_add.copy()
            order_product.quantity = order_product_quantity
            product_to_add.quantity = str(max(0, int(product_to_add.quantity) - order_product_quantity))  # Update product quantity

            order = Order()
            order.adding_product_warehouse(order_product)
            order.set_status("registered")
            self.orders.append(order)

            self.update_product_text_file()
            self.display_orders()
            self.display_products()
        else:
            messagebox.showerror("Error", "Invalid Product ID. Please enter a valid product ID.")                                  
    
    def removing_order_warehouse(self):
        # Prompt user to enter an order id to remove
        order_id_remove = simpledialog.askstring("Order Remove", "Enter Order Id to Remove:")

        # Iterate through orders to find the matching order
        for order in self.orders:
            if str(order.order_id) == order_id_remove:
                # Return products from the removed order back to the warehouse
                for product in order.products:
                    # Assuming you have a method to add the product back to the warehouse
                    self.add_product_back_to_warehouse(product)

                # Remove order and update display
                self.orders.remove(order)
                self.display_orders()
                self.display_products()

                messagebox.showinfo("Success", f"Order ID {order_id_remove} removed successfully from the warehouse")
                return

        # If no matching order is found
        messagebox.showerror("Error", f"Order ID {order_id_remove} not found.")

    def add_product_back_to_warehouse(self, product):
        # Find the existing product in the warehouse
        existing_product = next((p for p in self.products if p.product_id == product.product_id), None)

        if existing_product:
            # Add the quantity of the product back to the warehouse
            existing_product.quantity += product.quantity
            # Update the product text file
            self.update_product_text_file()
        else:
            # If the product doesn't exist in the warehouse, add it
            self.products.append(product.copy())
            # Update the product text file
            self.update_product_text_file()    

    #To see the information of the product
    def product_information_warehouse(self):
        #prompt use to use id or name to see the details
        product_inforamtion = simpledialog.askstring("Product Info", "Enter Product name or ID")

        #check if the  input is number
        if product_inforamtion.isdigit():
            # Search by product ID
            product_info = next((product for product in self.products if str(product.product_id)==product_inforamtion), None)
        else:
            # Search by product name        
            product_info = next((product for product in self.products if product.product_name == product_inforamtion), None)

        if product_info:
            #display details in message box
            product_details = (
                f"Product ID: {product_info.product_id}\n"
                f"Product Name: {product_info.name}\n"
                f"Product Quantity: {product_info.quantity}\n"
                f"Product Specification: {product_info.specification}\n"
                f"Product Last Ordered: {product_info.last_ordered}\n")
            messagebox.showinfo("Product Information", product_details)
        else:
            messagebox.showerror("Error", "Product not Found in the warehouse")

    #to see order information
    def order_information_warehouse(self):
        #prompt user Order id to see the details
        order_inforamtion = simpledialog.askstring("Order Info", "Enter Order ID")
        #check if the  input is number
        if order_inforamtion.isdigit():
            # Search by product ID
            order_info = next((order for order in self.orders if str(order.order_id)==order_inforamtion), None)
        else:
            order_inforamtion = None

        if order_inforamtion:
            #display details in message box
            order_details= (
                f"Order ID: f{order_info.order_id}\n"
                f"Status: f{order_info.status}\n"
                f"Accepted Time: f{order_info.time_accepted}\n"
                f"No of Products: f{order_info.products}\n"
                f"Product IDs: f{[product.product_id for product in order_info.products]}\n") 
            messagebox.showinfo("order Information", order_details)
        else:
            messagebox.showerror("Error", "Order not Found.")   

    #for Searching the product
    def search_product(self):
        #prompt use to use id or name to see the details
        product_identity = simpledialog.askstring("Search Product", "Enter Product name or ID:")

        #iterate through product to find the matching product
        matching_products = []
        for product in self.products:
            if product.name.lower() == product_identity.lower() or str(product.product_id) == product_identity:
                matching_products.append(product)

        if matching_products:
            # Display product information in a message box
            product_info = "\n".join([f"{attr}: {value}" for attr, value in matching_products[0].__dict__.items()])
            messagebox.showinfo("Product Information", product_info)
        else:
            messagebox.showerror("Error", "No product found for the specified name or ID.")

    #to put order in queue 
    def queue_by_order_id(self):
        #prompt user Order id to put in queue 
        order_id_queue = simpledialog.askstring("Queue Order", "Enter a Order ID to Queue")
        #iterate through the order to find the matching order
        for order in self.orders:
            if str(order.order_id) == order_id_queue:
                #Check if the order is already in queue
                if order.status == "registered":
                    order.set_status ('Queued')
                    self.display_orders()
                    #Show Success Message
                    messagebox.showinfo("Success", f"Order ID {order_id_queue} moved to queue.")
                else:
                    messagebox.showinfo("information", "Order is already in queue.")
                return

        #if no matching order is found
        messagebox.showerror("Error","Order not Found")


    def mark_collected_order_id(self):
        #prompt user Order id to put in collected
        order_id_mark_collected = simpledialog.askstring("Mark Collected", "Enter Order ID to mark as collected")

        #iterate to find the matching order
        for order in self.orders:
            if str(order.order_id) == order_id_mark_collected:
                if order.status == "Queued":
                    order.mark_collected()
                    self.display_orders()
                    #success message
                    messagebox.showinfo("Success", f"Order ID {order_id_mark_collected} marked as collected")
                else:
                    messagebox.showinfo("Information", "Order is not in Queue")
                return
        #if no matching order is found show error message
        messagebox.showinfo("Error", "Order not Found")            
                                

    #Function to remove order by id 
    def removing_order_warehouse_by_id(self):
        order_id = self.order_id_entry.get()
        for order in self.orders:
            if str(order.order_id) == order_id:
                for product in order.products:
                    product.quantity += product.quantity
                self.orders.remove(order) 

                self.display_orders()
                self.display_products()
                return

        messagebox.showerror("Error", "Order not Found")

    #Function to display the details of the product
    def display_product(self, product):
        self.product_text_box.insert(tk.END, f"Product ID: {product.product_id}\n")
        self.product_text_box.insert(tk.END, f"Name: {product.name}\n")
        self.product_text_box.insert(tk.END, f"Quantity: {product.quantity}\n")
        self.product_text_box.insert(tk.END, f"Specification: {product.specification}\n")
        self.product_text_box.insert(tk.END, f"last Ordered: {product.last_ordered}\n")
        self.product_text_box.insert(tk.END, "\n")

    def display_products(self):
        self.product_text_box.delete(1.0, tk.END)
        for product in self.products:
            self.display_product(product)

    def display_order(self, order):
        self.order_text_box.insert(tk.END, f"Order ID: {order.order_id}\n")  
        self.order_text_box.insert(tk.END, f"Status: {order.status}\n")         
        self.order_text_box.insert(tk.END, f"Time_Accepted: {order.time_accepted}\n")
        self.order_text_box.insert(tk.END, f"Time_Collecetd: {order.time_collected}\n")
        self.order_text_box.insert(tk.END, f"No of products: {len(order.products)}\n")
        self.order_text_box.insert(tk.END, f"Product IDs: {[product.product_id for product in order.products]}\n")  
        self.order_text_box.insert(tk.END, "\n")

    def display_orders(self):
        self.order_text_box.delete(1.0, tk.END)
        for order in self.orders:
            self.display_order(order)

    #to view the product log file
    def view_product_log_file(self):
        try:
            with open(Product.product_file, "r") as log_file:
                content = log_file.read()

            #window to see the product log content 
            log_window = tk.Toplevel(self.root)
            log_window.title("Product Log File")

            log_text_box = tk.Text(log_window, height=20, width=50, font='Helvetica 10', wrap=tk.WORD,bg='#EFEFEF', fg="#000000") 
            log_text_box.pack()

            log_text_box.insert(tk.END, content)
            log_text_box.config(state=tk.DISABLED)
        except FileNotFoundError:
            messagebox.showinfo("File not Found", "Product log file not found.")  

    #to view the order log file
    def view_order_log_file(self):
        try:
            with open(Order.log_file_order, "r") as log_file:
                content = log_file.read()

            #window to see the product log content 
            log_window = tk.Toplevel(self.root)
            log_window.title("Order Log File")

            log_text_box = tk.Text(log_window, height=20, width=50, font='Helvetica 10', wrap=tk.WORD,bg='#EFEFEF', fg="#000000") 
            log_text_box.pack()

            log_text_box.insert(tk.END, content)
            log_text_box.config(state=tk.DISABLED)
        except FileNotFoundError:
            messagebox.showinfo("File not Found", "Order log file not found.")   

    #To check the similarity
    def checking_similarity_warehouse(self):
    # prompt user to enter product name or id
        product_identifier = simpledialog.askstring("Check Similarity", "Enter Product name or id")

        if product_identifier:
            # Make sure to define self.specification_entry in your code
            current_specification = self.specification_entry.get().lower()
            similar_products = []

            for product in self.products:
                product_specification = product.specification.lower()
                if product.name.lower() != product_identifier.lower():
                    similarity_ratio = difflib.SequenceMatcher(None, current_specification, product_specification).ratio()
                    if similarity_ratio > 0.7:
                        similar_products.append((product, similarity_ratio))

            self.display_products()
            for product, similarity_ratio in similar_products:
                self.display_product(product)

            # display the result in the text box frame
            self.similarity_text_box.delete(1.0, tk.END)
            if similar_products:
                self.similarity_text_box.insert(tk.END, "Similar Products Found:\n")
                for product, similarity_ratio in similar_products:
                    self.similarity_text_box.insert(tk.END, f"{product.name} (ID: {product.product_id}) - Similarity: {similarity_ratio*100:.2f}%\n")
            else:
                self.similarity_text_box.insert(tk.END, "No similar products found.\n") 

    # to generate the pdf for the products
    def generate_pdf(self):
        try:
            with open(Product.product_file, "r") as log_file:
                content = log_file.readlines()

            # create pdf
            pdf_file = "PDF_Report.pdf"
            pdf_canvas = SimpleDocTemplate(pdf_file, pagesize=letter)

            # define table data
            table_data = [['Product ID', 'Product Name', 'Quantity', 'Last Updated']]

            for line in content:
                match = re.search(r"(\d+) \((\d+)\): Quantity=(\d+), Last Updated=(.+)", line)
                if match:
                    product_name = match.group(1)
                    product_id = int(match.group(2))
                    quantity = int(match.group(3))
                    last_updated = match.group(4)
                    if quantity > 0:
                        table_data.append([product_id, product_name, quantity, last_updated])

            # create table
            table = Table(table_data)
            style = TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, 0), (0.7, 0.7, 0.7)),
                    ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 0), (-1, 0), (1, 1, 1)),
                    ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),
                    ('TEXTCOLOR', (0, 0), (-1, -1), (0, 0, 0)),
                ]
            )

            table.setStyle(style)
            pdf_canvas.build([table])
            messagebox.showinfo("Report Generated", f"PDF Report {pdf_file} has been Generated")

        except FileNotFoundError:
            messagebox.showinfo("File Not Found", "Product log File Not Found")
 

    def generate_shopping_list_pdf(self):
        try:
            with open(Product.product_file, "r") as log_file:
                content = log_file.readlines()

            # create pdf
            pdf_file = "Shopping_List.pdf"
            pdf_canvas = SimpleDocTemplate(pdf_file, pagesize=letter)

            # define table data
            table_data = [['Product ID', 'Product Name', 'Quantity', 'Last Updated']]

            for line in content:
                match = re.search(r"(\d+) \((\d+)\): Quantity = (\d+), Last Ordered = (.+), Last Updated = (.+)", line)
                if match:
                    product_name = match.group(1)
                    product_id = int(match.group(2))
                    quantity = int(match.group(3))
                    last_ordered = match.group(4)
                    last_updated = match.group(5)
                    if quantity == 0:
                        table_data.append([product_id, product_name, quantity, last_updated])

            # create table
            table = Table(table_data)
            style = TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, 0), (0.7, 0.7, 0.7)),
                    ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 0), (-1, 0), (1, 1, 1)),
                    ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),
                    ('TEXTCOLOR', (0, 0), (-1, -1), (0, 0, 0)),
                ]
            )

            table.setStyle(style)
            pdf_canvas.build([table])
            messagebox.showinfo("Shopping List Generated", f"Shopping List PDF {pdf_file} has been Generated")

        except FileNotFoundError:
            messagebox.showinfo("File Not Found", "Product log File Not Found")        

    def update_product_text_file(self):
        with open(Product.product_file, "w") as log_file:
            for product in self.products:
                log_file.write(
                    f"{product.name} ({product.product_id}): Quantity = {product.quantity}, "
                    f"Last Ordered = {product.last_ordered}, Last Updated = {datetime.now()}\n")
         



root = tk.Tk()
Warehouse = warehouse(root)
root.mainloop()