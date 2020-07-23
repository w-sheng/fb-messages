import json
import os
import pandas as pd
import re
import sys

from datetime import datetime
from matplotlib import pyplot as plt

################################################################################
################################################################################

class Contact():
	def __init__(self, name):
		self.name = name
		self.total_messages = 0
		self.ind_messages = 0
		self.group_messages = 0
		self.num_groups = 0
		self.group_chats = set()

		# variables for dataframes
		self.df_dicts = [] # list of dictionaries to construct dataframe later
		self.df = pd.DataFrame()

	def update_groups(self, chat_name):
		self.group_chats.add(chat_name)

	def add_df_dict(self, dict):
		self.df_dicts.append(dict)

	def finalize(self):
		self.df = pd.DataFrame(self.df_dicts)
		self.total_messages = len(self.df)
		self.group_messages = len(self.df[self.df['is_group']])
		self.ind_messages = self.total_messages - self.group_messages
		self.num_groups = len(self.group_chats)

	def graph_by_month(self):
		df = self.df
		df['date'] = pd.to_datetime(df.date)
		df = df.sort_values(by='date')
		df['month'] = df['date'].dt.strftime('%Y-%m')
		del df['date']

		# group data by month
		group_df = df[df['is_group'] == True].groupby('month')['is_group'].count()
		ind_df = df[df['is_group'] == False].groupby('month')['is_group'].count()
		sent_df = df[df['is_sender'] == True].groupby('month')['is_sender'].count()

		# join dataframes
		agg_df = pd.merge(ind_df,group_df, on = 'month', how = 'outer').reset_index()
		agg_df = agg_df.fillna(0)
		agg_df.columns = ['month','ind_messages','group_messages']
		agg_df['all_messages'] = agg_df['ind_messages'] + agg_df['group_messages']
		agg_df = agg_df.sort_values('month', ascending=True)
		agg_df = agg_df.set_index('month')

		# draw graph
		agg_df.plot(color = ['springgreen','deepskyblue','salmon'])
		plt.legend(['1:1','Group','Total'])
		plt.title(self.name)
		plt.xticks(range(len(agg_df.index)), agg_df.index, rotation=90)
		plt.ylabel('Number of messages')
		plt.ylim(ymin = 0.0)
		plt.tight_layout()
		plt.show()

	def print_stats(self):
		print('\n' + self.name)
		print('Total messages:\t' + "{:,}".format(self.total_messages))
		print('1:1 messages:\t' + "{:,}".format(self.ind_messages))
		print('Group messages:\t' + "{:,}".format(self.group_messages))
		print('Group chats:\t' + "{:,}".format(self.num_groups))

	def print_group_chats(self):
		for gc in self.group_chats:
			print('  - ' + gc)


################################################################################
################################################################################

def iter_directory(directory, chat_limit, contacts):
	print(directory)
	for folder in os.listdir(directory):
		if folder != '.DS_Store':
			subdir = directory + '/' + folder # subdir = a single chat

			for f in os.listdir(subdir): 
				if 'message' in f: # finding message_N.json files
					chat_json = open(subdir + '/' + f)
					data = json.load(chat_json)

					# discard huge groups
					if len(data['participants']) <= chat_limit: 
						parse_chat(folder, data, contacts)

def parse_chat(chat_name, data, contacts):
	''' chat_name = name of group chat,
		data = json representation of chat,
		contacts = dictionary representation of all contacts
	'''
	participants = []
	for p in data['participants']:
		name = p['name']
		participants.append(name)

		if name not in contacts:
			new_contact = Contact(name)
			contacts[name] = new_contact
	
	messages = data['messages']
	num_messages = len(messages)
	is_group = len(participants) > 2

	if is_group:
		regex = re.search('(.*)_.*', chat_name)
		if regex:
			chat_name = regex.group(1)

		for name in participants:
			contacts[name].update_groups(chat_name)

	for m in messages:
		sender = m['sender_name']
		date_ms = m['timestamp_ms']
		date = datetime.fromtimestamp(date_ms/1000.0).strftime('%Y-%m-%d %H:%M:%S')
		content = ''
		if 'content' in m.keys():
			content = m['content']

		# update df_dicts list of each participant
		for name in participants:
			row_dict = {}
			row_dict['date'] = date
			row_dict['is_group'] = is_group

			is_sender = name == sender
			row_dict['is_sender'] = is_sender

			contact = contacts[name]
			contact.add_df_dict(row_dict)


################################################################################
################################################################################

if __name__ == '__main__':
	self_name = sys.argv[1]
	group_limit = int(sys.argv[2])

	contacts = {} # create dict (key = name, value = contact obj)
	contacts[self_name] = Contact(self_name) # add yourself to dict

	# iterate through all directories to get all chats
	directories = sys.argv[3:]
	for d in directories:
		directory = d + '/inbox'
		iter_directory(directory, group_limit, contacts)

	# finalize and sort all contacts
	for c in contacts.values():
		c.finalize()
	sorted_contacts = sorted(contacts.items(), key=lambda x: x[1].total_messages, reverse=True)

	# display your overall messaging stats
	print('\n================ YOUR STATS ================')
	contacts[self_name].print_stats()
	print('Unique people messaged: ' + str(len(contacts) - 1))

	# display distribution of number of messages for top 50 contacts
	names = [] 
	freqs = []
	for (n,c) in sorted_contacts[1:50]:
		names.append(n)
		freqs.append(c.total_messages)

	plt.figure(figsize=(8,6))
	plt.bar(names, freqs, color='deepskyblue')
	plt.xticks(rotation=90)
	plt.ylabel('Number of messages')
	plt.tight_layout()
	plt.show()

	# display top 10 most contacted people
	print('\n================== TOP 10 ==================')
	for (_,c) in sorted_contacts[1:10]:
		c.print_stats()

	# prompt for input to display detailed stats of a contact
	print('\n============================================')
	is_running = True
	input_text = raw_input('\nEnter a name for detailed stats:\n')
	while is_running:
		if input_text in contacts:
			input_contact = contacts[input_text]
			input_contact.print_stats()
			input_contact.print_group_chats()
			input_contact.graph_by_month()
		else:
			print('Invalid name :(')

		continue_text = '\nEnter another name, or type q if you\'re done:\n'
		input_text = raw_input(continue_text)
		is_running = False if (input_text == 'q') else True

