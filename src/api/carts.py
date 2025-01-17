import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    #getting the offset 
    if search_page == "":
        n = 0
    else: 
        print("search_page: " + str(search_page))
        n = int(search_page)
    next = ""
    prev = ""
    # print("customer name: " + customer_name)
    # print("potion sku: " + potion_sku)
    # print("search_page: " + search_page)
    # print("sort_col: " + sort_col)
    # print("sort_order: " + sort_order) #will either be desc or asc 
    if sort_col is search_sort_options.customer_name:
        order_by = "carts.customer"
    elif sort_col is search_sort_options.item_sku:
        order_by = "potions.sku"
    elif sort_col is search_sort_options.line_item_total:
        order_by = "cart_items.quantity"
    elif sort_col is search_sort_options.timestamp:
        order_by = "cart_items.created_at"
    else: 
        assert False

    if sort_order == search_sort_order.asc:
        order_by += " ASC"
    elif sort_order == search_sort_order.desc: 
        order_by += " DESC"
    
    
    # if customer_name != "":
    #     stmt = stmt.where(db.carts.customer.ilike(f"%{customer_name}%"))

    with db.engine.connect() as connection: 
        # result = connection.execute(sqlalchemy.text("""SELECT carts.id, carts.customer, potions.sku, potions.price, cart_items.quantity, cart_items.created_at FROM carts INNER JOIN cart_items ON carts.id = cart_items.cart_id INNER JOIN potions ON potions.id = cart_items.potion_id ORDER BY :orderBy :ascdesc"""),[{"orderBy": order_by, "ascdesc": sort_order.value.upper()}])
        # result = sqlalchemy.text("""SELECT carts.id, carts.customer, potions.sku, potions.price, cart_items.quantity, cart_items.created_at FROM carts INNER JOIN cart_items ON carts.id = cart_items.cart_id INNER JOIN potions ON potions.id = cart_items.potion_id ORDER BY {}""".format(order_by))
        result = """SELECT carts.id, carts.customer, potions.sku, potions.price, cart_items.quantity, cart_items.created_at FROM carts INNER JOIN cart_items ON carts.id = cart_items.cart_id INNER JOIN potions ON potions.id = cart_items.potion_id"""
        customer_col = ""
        potion_col = ""
        if customer_name != "":
            customer_col = "carts.customer"
            result += f" WHERE {customer_col} ILIKE :name"
            params = {"name": f'%{customer_name}%'}
        else:
            params = {}
        if potion_sku != "":
            if "WHERE" in result:
                result += " AND "
            else: 
                result += " WHERE "
            potion_col = "potions.sku"
            result += f"{potion_col} ILIKE :sku"
            params["sku"] = f'%{potion_sku}%'

        result += f" ORDER BY {order_by}"
        result = connection.execute(sqlalchemy.text(result), params)   
        # result = connection.execute(sqlalchemy.text(result))

        result = result.fetchall()
        # if customer_name != "":
        #     result = result.filter(db.carts.c.customer.ilike(f'%{customer_name}'))
        # if potion_sku != "":
        #     result = result.filter(db.potions.c.sku.ilike(f'%{potion_sku}'))
        for item in result: 
            print(item.id)
            print(item.sku)
            print(item.customer)
            print(item.quantity)
            print(item.created_at)

        if n >= 5: 
            prev = str(int(search_page) - 5)

        if len(result) > 5: 
            if (prev == ""):
                next = 5
            else: 
                next = str(n + 5)


        
        returned = []
        # i = int(search_page)
        i = 0
        for item in range(n + 1, n + 6): 
            if item >= len(result):
                next = ""
                break
            print(i)

            returned.append({
                "line_item_id": result[item].id,
                "item_sku": result[item].sku,
                "customer_name": result[item].customer,
                "line_item_total": result[item].price * result[item].quantity,
                "timestamp": result[item].created_at,
            })        
        length = len(result)
        print("length: " + str(length))


    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": prev,
        "next": next,
        "results": returned,
    }


class NewCart(BaseModel):
    customer: str


@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    print("customer:")
    print(new_cart.customer)
    #insert row for new cart
    value = {'name':new_cart.customer}
    with db.engine.begin() as connection: 
        result = connection.execute(sqlalchemy.text("INSERT INTO carts (customer) VALUES (:name) RETURNING id"), [{'name':new_cart.customer}])
    print("cartID")
    result = result.fetchone()
    print(result[0])
    return {"cart_id": result[0]}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """  
    # with db.engine.begin() as connection: 
    #     result = connection.execute(sqlalchemy.text("SELECT "))
    # with db.engine.begin() as connection: 
    #     result = connection.execute(sqlalchemy.text("SELECT * FROM cart_items WHERE cart_id=:id"), {"id": cart_id})
        
    return 
    # return cart_memory.get(cart_id)
    # return [
            # {
            #     "potion_type": [100, 0, 0, 0],
            #     "quantity": 0,
            # }
    #     ]


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection: 
        potionID = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE sku=:itemsku"), {'itemsku':item_sku})
        potionID = potionID.fetchone()
        print("potionID ->  " + str(potionID.id))
        print("qty:")
        quantity = connection.execute(sqlalchemy.text("SELECT SUM(change) AS balance FROM potion_ledger WHERE potion_id = :id"), {'id': potionID.id})
        quantity = quantity.fetchone()
        quantity = quantity.balance
        print(cart_item.quantity)
        if cart_item.quantity < quantity:
            connection.execute(sqlalchemy.text("INSERT INTO cart_items (potion_id, cart_id, quantity) VALUES (:potID, :cartID, :qty)"), {'potID':potionID.id, 'cartID':cart_id, 'qty':cart_item.quantity})
            return "OK"
        else: 
            return "QUANTITY TOO HIGH"

class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    print("payment: ")
    print(cart_checkout.payment)
    total_potions = 0
    total_price = 0
    with db.engine.begin() as connection: 
        result = connection.execute(sqlalchemy.text("SELECT cart_items.cart_id, cart_items.quantity, cart_items.potion_id, potions.price, potions.sku FROM cart_items LEFT JOIN potions ON cart_items.potion_id = potions.id WHERE cart_id = :cart_id"), 
                                    {"cart_id": cart_id})
        for item in result:
            potionID = item.potion_id
            qty = item.quantity
            total_potions += item.quantity
            payment = item.price * item.quantity
            total_price += payment
            print("payment: " + str(payment))
            print("current total_potions is: ")
            print(total_potions)
            print("potion ID")
            print(potionID)
            print("qty")
            print(qty)
            print("right before the supposed problem")
            # potionType = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE id=:potion_id"), {'potion_id': potionID})
            # potionType = potionType.fetchone()
            print("potion sku")
            print(item.sku)
            print("you're buying " + item.sku)
            connection.execute(sqlalchemy.text("INSERT INTO potion_ledger (change, potion_id) VALUES (:ch, :potID)"), {'ch':-(item.quantity), 'potID': potionID})                
            
            ledgeID = connection.execute(sqlalchemy.text("INSERT INTO gold_ledger (change) VALUES (:ch) RETURNING id"), {'ch':payment})
            ledgeID = ledgeID.fetchone()
            ledgeID = ledgeID.id

            desc = f'Bought {qty} of {item.sku} with gold ledge id of {ledgeID}'
            print(desc)
            connection.execute(sqlalchemy.text("INSERT INTO transactions (description) VALUES (:desc)"), {'desc': desc})

    print("total gold paid is: "  + str(total_price))
    return {"total_potions_bought": total_potions, "total_gold_paid": total_price}