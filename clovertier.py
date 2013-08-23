#!/usr/bin/python

'''
I think you need the following categories to make this game functional:
drinks
equipment
toys
corgi goodies
'''

from clover_api import *
import random
import calendar
import datetime
import api_token

CloverAPI.base_url = 'https://www.clover.com'
c = CloverAPI(api_token.TOKEN, merchant_id=api_token.MERCHANT_ID)

TIME_REMAINING = 480
TIME_DEBUG = False
DEBT = 4000

def haggle(item, customer):
	base_price = item['base_price']
	approve = base_price * customer['approve']
	reject = base_price * customer['reject']
	leave = base_price * customer['leave']
	haggles = 3
	print
	print build_response(customer['first_name'], customer['flavor_intro'])
	print "base price: {0} pix".format(str(base_price))
	while (haggles >= 0): # let the initial offer be the zeroth haggle
		offer = int(raw_input('capitalism, ho!: '))
		print
		if offer <= approve:
			print build_response(customer['first_name'], customer['flavor_great'])
			break
		elif approve < offer and offer < reject:
			if random.random() < customer['p_approve']:
				print build_response(customer['first_name'], customer['flavor_ok'])
				break
			else:
				print build_response(customer['first_name'], customer['flavor_ng'])
				reject = offer
				haggles -= 1
		elif reject <= offer and offer < leave:
			print build_response(customer['first_name'], customer['flavor_bad'])
			haggles -= 1
		else:
			haggles = -1

	if haggles == -1:
		print build_response(customer['first_name'], customer['flavor_leave'])
		print '\n\n\n'
		offer = None

	if offer is None:
		return

	print '{0} was sold for {1} pix, {2}% of base price!\n\n\n'.format(item['name'], str(offer), str(offer * 100 / base_price))

	order_uuid = c.post('/v2/merchant/{mId}/orders', { }).uuid
	c.post('/v2/merchant/{mId}/orders/{orderId}/state', {"state": "OPEN"}, orderId=order_uuid)
	c.post('/v2/merchant/{mId}/orders/{orderId}/total', {"total": offer}, orderId=order_uuid)
	c.post('/v2/merchant/{mId}/orders/{orderId}/customer', {"customerUuid": customer['id']}, orderId=order_uuid)

def get_item_to_suggest():
	items_response = c.get('/v2/merchant/{mId}/inventory/items_with_categories')
	print 'clo: (hmm... i have these:'
	for item in items_response.items:
		print '    <{0}> in {1} at ${2}'.format(item.name, item.categories[0].name, item.price / 100)
	item_name = raw_input('what should i choose?) ')
	return next((item for item in items_response.items if item.name == item_name), 'junk')

def build_response(name, flavor):
	return name + ": " + flavor

def get_random_category(customer):
	categorical_needs = set(customer['categorical_needs'])
	categories_response = c.get('/v2/merchant/{mId}/inventory/categories')
	all_categories = set(category.name for category in categories_response.categories)
	possible_categories = tuple(categorical_needs & all_categories)
	max_index = len(possible_categories) - 1
	random_index = random.randint(0, max_index)
	return possible_categories[random_index]

def get_total(start_time, end_time):
	orders_response = c.get('/v2/merchant/{mId}/orders' + '?start_time={0}&end_time={1}'.format(str(start_time), str(end_time)))
	total = 0
	for order in orders_response.orders:
		total += order.total # why can't i even modify paid?!
	return total

def order_by_grand_total_desc(a, b):
	return b['grand_total'] - a['grand_total']

def print_customer_summaries(start_time, end_time):
	customers_response = c.get('/v2/merchant/{mId}/customers')
	cids = [cust.id for cust in customers_response.customers]
	report = []
	for cid in cids:
		customer_response = c.get('/v2/merchant/{mId}/customers/{customerId}', customerId=cid)
		name = customer_response.customer.firstName
		grand_total = sum(order.total for order in customer_response.customer.orders if start_time <= order.createdTime and order.createdTime <= end_time)
		report.append({'name': name, 'grand_total': grand_total})
	report.sort(order_by_grand_total_desc)
	print 'my favorite customers'
	for row in report:
		print '{0:13} {1:13}'.format(row['name'], row['grand_total'])
	print '\n\n'
	

def add_customer_ids(customers):
	customers_response = c.get('/v2/merchant/{mId}/customers')
	for customer in customers:
		customer['id'] = next(cust.id for cust in customers_response.customers if cust.firstName == customer['first_name'])

def get_time_to_decrement_by():
	if TIME_DEBUG:
		return 1
	else:
		return random.randint(45, 75)

def main():
	customers = build_customers()
	add_customer_ids(customers)

	clo_welcome = { \
		'jacques': '(oh great, it\'s jacques)', \
		'leonard': 'hey, it\'s my favorite customer leonard! howya doing?', \
		'annie': 'hi, annie. how may i help you?'
	}

	time_remaining = TIME_REMAINING - get_time_to_decrement_by()
	print 'vertier: you owe me {0} pix today. get to work!\n'.format(str(DEBT))

	start_time = calendar.timegm(datetime.datetime.utcnow().utctimetuple())*1000
	while (time_remaining > 0):
		print "{0} minutes to closing".format(time_remaining)
		customer_index = random.randint(0, len(customers) - 1)
		customer = customers[customer_index]
		#customer = customers[1]
		print build_response('clo', clo_welcome[customer['first_name']])
		category = get_random_category(customer)
		print build_response(customer['first_name'], customer['flavor_categories'][category])
		raw_item = get_item_to_suggest()
		if raw_item == 'junk' or raw_item.categories[0].name != category or raw_item.price > customer['budget']:
			print build_response(customer['first_name'], customer['flavor_categories']['wrong'] + '\n\n\n')
		else:
			item = {'name': raw_item.name, 'base_price': raw_item.price}
			haggle(item, customer)

		time_remaining -= get_time_to_decrement_by()
	end_time = calendar.timegm(datetime.datetime.utcnow().utctimetuple())*1000
	total = get_total(start_time, end_time)
	print_customer_summaries(start_time, end_time)
	if total > DEBT:
		print 'clo: all right, i have {0} pix!'.format(str(total))
		print 'vertier: congrats, you get to live for another day!'
		print '\n\n\nSEE YOU TOMORROW\n\n\n'
	else:
		print 'clo: i only have {0} pix...'.format(str(total))
		print 'vertier: hope you like the streets, because you\'re going to be out there for a long, long time...\n'
		print 'and so... clo was crushed by the cruel bitterness of reality'
		print 'his home, a spacious cardboard box'
		print 'i cry every time'
		print '\n\n\nGAME OVER\n\n\n'

def build_customers():
	jacques = { \
		'first_name': 'jacques', \
		'approve': .5, 'reject': 1.1, 'leave': 1.25, 'p_approve': .4, \
		'budget': 1000, \
		'flavor_intro': 'how much?', \
		'flavor_great': 'now that\'s what i\'m talking about', \
		'flavor_ok': 'ok...', \
		'flavor_ng': 'wtf?', \
		'flavor_bad': 'ffs...', \
		'flavor_leave': 'i\'m going to gtfo', \
		'categorical_needs': ('drinks', 'equipment'), \
		'flavor_categories': \
			{'drinks': 'i\'m thirsty. what do we have here...', \
			 'equipment': 'i need something for my server room', \
			 'wrong': 'wtf is this?! *walks out*'}
	}
	leonard = { \
		'first_name': 'leonard', \
		'approve': .9, 'reject': 2.5, 'leave': 8, 'p_approve': .7, \
		'budget': 5000, \
		'flavor_intro': 'that\'s so awesome. i\'d pay lots for it', \
		'flavor_great': 'wow, much appreciated', \
		'flavor_ok': 'decent price. i\'ll take it', \
		'flavor_ng': 'well, maybe for a lower price', \
		'flavor_bad': 'i don\'t know~', \
		'flavor_leave': 'do you honestly think i\'m made of money? well, yes, but i\'ll take my money elsewhere', \
		'categorical_needs': ('toys',), \
		'flavor_categories': \
			{'toys': 'i want something cool. for the office.', \
			 'wrong': 'that does not amaze me at all. *sighs and leaves*'}
	}
	annie = { \
		'first_name': 'annie', \
		'approve': .6, 'reject': 1.3, 'leave': 1.6, 'p_approve': .55, \
		'budget': 2000, \
		'flavor_intro': 'that looks good', \
		'flavor_great': 'awesome! thank you', \
		'flavor_ok': 'it\'ll have to do...', \
		'flavor_ng': 'that\'s too much', \
		'flavor_bad': 'really?', \
		'flavor_leave': 'ugh, i give up', \
		'categorical_needs': ('drinks', 'corgi goodies'), \
		'flavor_categories': \
			{'drinks': 'need something to keep me awake...', \
			 'corgi goodies': 'i feel like pampering my corgi today', \
			 'wrong': 'no... i\'ll try somewhere else. bye~'}
	}

	return [jacques, leonard, annie]


if __name__ == '__main__':
	print '\n\n\n'
	print 'WELCOME TO CLOVERTIER'
	print 'BE MY GUEST'
	print 'ANOTHER DAY, ANOTHER BUY'
	print 'BUT REMEMBER'
	print 'SELL OR DIE'
	print 'AHHH HA HA HA HA HA HA'
	print '    ~ vertier'
	print '\n\n\n'
	main()
