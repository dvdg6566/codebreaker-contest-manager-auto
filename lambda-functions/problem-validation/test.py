import lambda_function

obj = {'problemName': 'simplebridges'}

resp = lambda_function.lambda_handler(obj,None)

print(resp)