from analyzer import *
from os import path
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import ttk

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# tkinter set-up
window = Tk()
window.title('Messenger Analytics')
style = ttk.Style()
style.configure('.', bg='white')
style.configure('TNotebook.Tab', bg='white')

# ==============================================================================
# variables and set-up
# ==============================================================================

uploaded_dirs = []
uploaded_dirs_str = 'No files uploaded'
contacts = {} # create dict (key = name, value = contact obj)
sorted_contacts = [] # empty list of contacts, sorted by num messages
self_name = ''
group_limit = 150 # fb group chat max size

def update_uploaded_dirs(new_dir):
	global uploaded_dirs
	global uploaded_dirs_str

	uploaded_dirs.append(new_dir)
	if (uploaded_dirs_str == 'No files uploaded'):
		uploaded_dirs_str = new_dir
	else:
		uploaded_dirs_str += '\n' + new_dir


# ==============================================================================
# tab menu
# ==============================================================================

tab_menu = ttk.Notebook(window)
tab1 = ttk.Frame(tab_menu)
tab2 = ttk.Frame(tab_menu)
tab3 = ttk.Frame(tab_menu)
tab4 = ttk.Frame(tab_menu)
tab5 = ttk.Frame(tab_menu)

tab_menu.add(tab1, text='Set-Up')
tab_menu.add(tab2, text='Your Stats')
tab_menu.add(tab3, text='Top')
tab_menu.add(tab4, text='Search')
tab_menu.add(tab5, text='All')

# ==============================================================================
# "Your Stats" tab
# ==============================================================================

title_stats = Label(tab2, text='go upload smthing first ¯\\_(ツ)_/¯', font=(None,16,'bold'), padx=5, pady=5)
title_stats.grid(columnspan=10, sticky=W)

lbl_stats = Label(tab2, text='', font=(None,14), justify=LEFT)
lbl_stats.grid(columnspan=10, pady=10, sticky=W)

# messaging distribution of top N contacts
lbl_top = Label(tab2, text='Display top N:', font=(None,14))
lbl_top.grid(row=3, pady=(10,0), sticky=W)
top_instr = 'For plotting the messaging distribution of your top N most messaged contacts.'
sublbl_top = Label(tab2, text=top_instr, font=(None,9), justify=LEFT)
sublbl_top.grid(columnspan=10, row=4, sticky=W)

default_N = DoubleVar(value=50)
input_N = Spinbox(tab2, width=5, textvariable=default_N)
input_N.grid(column=1, row=3, pady=(10,0), sticky=W)

fig_top = Figure(figsize=(8,6), tight_layout=True)
ax_top = fig_top.add_subplot(111)
canvas_top = FigureCanvasTkAgg(fig_top, master=tab2)

# plot distribution of top N contacts
def plot_top_N():
	n = int(input_N.get())
	names = [] 
	freqs = []
	for (n,c) in sorted_contacts[1:(n+1)]:
		names.append(n)
		freqs.append(c.total_messages)

	ax_top.clear()
	ax_top.set_title('Top ' + input_N.get() + ' Contacts')
	ax_top.bar(names, freqs, color='deepskyblue')
	ax_top.tick_params(axis='x', rotation=90)
	ax_top.set_ylabel('Number of messages')
	
	canvas_top.draw()
	plot_widget = canvas_top.get_tk_widget()
	plot_widget.grid(columnspan=10)


# ==============================================================================
# "Top" tab
# ==============================================================================

title_top = Label(tab3, text='Top 10', font=(None,16,'bold'), padx=5, pady=5)
title_top.grid(sticky=W)

txt_top = scrolledtext.ScrolledText(tab3, width=50, font=(None,14))
txt_top.grid(sticky=W)


# ==============================================================================
# "Search" tab
# ==============================================================================

title_search = Label(tab4, text='Search', font=(None,16,'bold'), padx=5, pady=5)
title_search.grid(columnspan=10, sticky=W)
search_instr = 'Search a specific person\'s name for stats, a list of group chats, and a plot of messages sent over time. You can search yourself too!'
sublbl_search = Label(tab4, text=search_instr, font=(None,9), justify=LEFT)
sublbl_search.grid(columnspan=10, sticky=W)

name_input = Entry(tab4, width=15)
name_input.grid(pady=(10,0), sticky=W)

chk_state = IntVar()
chk_breakdown = Checkbutton(tab4, text='Include 1:1/Group breakdown', variable=chk_state)
chk_breakdown.grid(sticky=W)

search_stats = scrolledtext.ScrolledText(tab4, width=50, font=(None,14))

# timeseries
fig_search = Figure(figsize=(8,5), tight_layout=True)
ax_search = fig_search.add_subplot(111)
canvas_search = FigureCanvasTkAgg(fig_search, master=tab4)

def plot_timeseries(contact, incl_breakdown):
	contact.make_timeseries_df()
	agg_df = contact.agg_df

	ax_search.clear()
	if incl_breakdown:
		agg_df.plot(ax=ax_search, color=['springgreen','deepskyblue','salmon'])
	else:
		agg_df['total'].plot(ax=ax_search, color='salmon')

	ax_search.set_title('Messages over time: ' + contact.name)
	ax_search.set_xticks(range(len(agg_df.index)))
	ax_search.set_xticklabels(agg_df.index, rotation=90)
	ax_search.set_ylabel('Number of messages')

	canvas_search.draw()
	plot_widget = canvas_search.get_tk_widget()
	plot_widget.grid(columnspan=10, column=10, row=4)


def get_stats():
	search_name = name_input.get()
	search_stats.delete('1.0', END)
	if search_name in contacts:
		input_contact = contacts[search_name]
		stats_text = input_contact.name + '\n\n' + input_contact.get_stats() + '\n\nGroup chats:\n' + input_contact.get_group_chats()
		search_stats.insert(INSERT, stats_text)
		plot_timeseries(input_contact, chk_state.get())
	else:
		search_stats.insert(INSERT, 'Invalid name :(')
	search_stats.grid(columnspan=10, column=0, row=4, padx=(15,0), pady=10, sticky=W)

btn_search = Button(tab4, text='Get stats', command=get_stats)
btn_search.grid(row=5, pady=5, sticky=W)


# ==============================================================================
# "All" tab
# ==============================================================================

title_all = Label(tab5, text='All', font=(None,16,'bold'), padx=5, pady=5)
title_all.grid(sticky=W)
all_descr = 'Every person you\'ve messaged and the total number of messages you have with them.'
subtitle_all = Label(tab5, text=all_descr, font=(None,9))
subtitle_all.grid(columnspan=10, pady=(0,10), sticky=W)

txt_all = scrolledtext.ScrolledText(tab5, width=50, font=(None,14))
txt_all.grid(sticky=W)


# ==============================================================================
# "Set-Up" tab
# ==============================================================================

# input name
lbl_name = Label(tab1, text='Enter your name:', font=(None,14))
lbl_name.grid(sticky=W)
input_name = Entry(tab1, width=15)
input_name.grid(column=1, row=0, pady=10, sticky=W)

# upload directories
title_up = Label(tab1, text='Upload your FB directories:', font=(None,14))
title_up.grid(sticky=W)
subtitle_up = Label(tab1, text='(You can upload 1 or more directories)', font=(None,9))
subtitle_up.grid(sticky=W)
lbl_up = Label(tab1, text=uploaded_dirs_str, font=(None,14))
lbl_up.grid(columnspan=10, pady=10, sticky=W)

def select_dir():
	dir_up = filedialog.askdirectory(initialdir=path.dirname(path.abspath(__file__)))
	update_uploaded_dirs(dir_up)
	lbl_up.config(text=uploaded_dirs_str)

btn_upload = Button(tab1, text='Upload', command=select_dir, highlightbackground='gray')
btn_upload.grid(column=1, row=1, sticky=W)

# group chat limit
lbl_limit = Label(tab1, text='Enter group chat limit:', font=(None,14))
lbl_limit.grid(sticky=W)
input_limit = Spinbox(tab1, from_=3, to=150, width=5) # fb chat max size = 150
input_limit.grid(column=1, row=4, sticky=W)
limit_instr = 'A group chat max number of participants limit. You probably don\'t *really*\ntalk to anyone in a group chat of 50 people, so you can choose to discard\nlarge group chats like that. The inputted group chat limit n is inclusive\n(e.g., it includes group chats with <=n participants).'
sublbl_limit = Label(tab1, text=limit_instr, font=(None,9), justify=LEFT)
sublbl_limit.grid(columnspan=10, sticky=W)

lbl_status = Label(tab1, text='Done analysis! :)', font=(None,14,'italic'), fg='blue')


# ==============================================================================
# the actual analysis!!!!!!
# ==============================================================================
def analyze():
	global contacts
	global sorted_contacts
	global self_name
	global group_limit
	global uploaded_dirs

	contacts = {} # reset contacts
	self_name = input_name.get()
	contacts[self_name] = Contact(self_name)
	group_limit = int(input_limit.get())

	# parse all chats
	for d in uploaded_dirs:
		directory = d + '/inbox'
		iter_directory(directory, group_limit, contacts)

	# sort all contacts
	for c in contacts.values():
		c.finalize()
	sorted_contacts = sorted(contacts.items(), key=lambda x: x[1].total_messages, reverse=True)

	# --------------------------------------------------------------------------
	# update other tabs
	# --------------------------------------------------------------------------
	if self_name in contacts:

		# YOUR STATS TAB
		title_stats.config(text=self_name)
		stats = contacts[self_name].get_solo_stats(len(contacts) - 1)
		lbl_stats.config(text=stats)
		btn_top = Button(tab2, text='Plot!', command=plot_top_N, highlightbackground='gray')
		btn_top.grid(column=2, row=3, pady=(10,0), sticky=W)
		
		# TOP 10 TAB
		top10 = ''
		i = 1
		for (_,c) in sorted_contacts[1:11]:
			top10 += str(i) + '. ' + c.name.upper() + '\n' + c.get_stats() + '\n\n'
			i += 1
		txt_top.delete('1.0', END)
		txt_top.insert(INSERT, top10)

		# ALL TAB
		j = 1
		all_ppl = 'Number of people messaged: ' + str(len(contacts) - 1) + '\n\n'
		for (_,c) in sorted_contacts[1:]:
			all_ppl += str(j) + '. ' + c.name + '\t\t\t' + "{:,}".format(c.total_messages) + '\n'
			j += 1
		txt_all.delete('1.0', END)
		txt_all.insert(INSERT, all_ppl)

	lbl_status.grid(pady=5, sticky=W)


btn_start = Button(tab1, text='Analyze!!', command=analyze, highlightbackground='gray')
btn_start.grid(pady=15, sticky=W)


# ==============================================================================
# window management
# ==============================================================================

def _quit():
	window.quit()
	window.destroy()

tab_menu.pack(expand=1, fill='both')
window.mainloop()