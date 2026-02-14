import uuid

class Expense:
    def __init__(self, date, category, amount, payment_method, rebate=0.0, id =None):
        self.id = id or str(uuid.uuid4())
        self.date = date
        self.category = category
        self.amount = float(amount)
        self.payment_method = payment_method
        self.rebate = float(rebate)
            
    def to_dict(self):
        return{
            
            "id":self.id,
            "date":self.date,
            "category":self.category,
            "amount":self.amount,
            "payment_method":self.payment_method,
            "rebate":self.rebate
        }
        
    def to_String(self):
        print(
            f"{self.id}|{self.date}|{self.category}|{self.amount}|{self.payment_method}|{self.rebate}"
        )
        
    @staticmethod
    def from_dict(data):
        return Expense(
            id=data["id"],
            date=data["date"],
            category=data["category"],
            amount=data["amount"],
            payment_method=data["payment_method"],
            rebate=data["rebate"]
            
        )