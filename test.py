from .XMLApi_interspire import API

api = API('https://emkt14.netnam.vn/xml.php', 'demo', '9efea42270c3e7315533aadaeec5fe6bf9815f77')

print(api.get_lists())