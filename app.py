import mysql.connector #run to test connection
import streamlit as st
import pandas as pd

#FUNCTIONS--------------------

#Try initializing session state --> only on the first run thru
if "jobs_showing" not in st.session_state :
    st.session_state.jobs_showing = False

#Try initializing session state --> only on the first run thru
if "saved_jobs" not in st.session_state :
    st.session_state.saved_jobs = False

#Try connecting to the database 'mydatabase'
mydb = mysql.connector.connect(
  host="localhost",
  user="XXXXXX",
  password= "XXXXXXX"
  database = "mydatabase"
)

#print("Successfully connected to db")
mycursor = mydb.cursor()

#select query
@st.cache #Doesn't keep doing this over and over again!
def select_query(sql):
    mycursor.execute(sql)
    field_names = [i[0] for i in mycursor.description]
    #("FIELD NAMES: ", field_names)
    df = pd.DataFrame(mycursor.fetchall(), columns=field_names) #dataframe and columnnames
    return df

#find company from id query
def company_name_from_id(company_id):
    mycursor.execute(f"""
    SELECT company_name 
    FROM companies 
    WHERE company_id = {company_id}
    """)
    company_name = mycursor.fetchall()
    for row in company_name:
        return row[0]

#mysql column to python list
def column_to_list(table_name, column_name, duplicates):
    mycursor.execute(f"""
    SELECT {column_name} 
    FROM {table_name} 
    """)
    column_list = []
    column_values = mycursor.fetchall()
    for row in column_values:
        column_list.append(row[0])
    if duplicates == 0:
        column_list_no_duplicates = list(set(column_list))
        return column_list_no_duplicates

    return column_list

#mysql query creator for single table with subquery
def query_creator(table_name, columns, search_lists, order_by): #jobs, ["job_title", "job_location"], [["Real Estate Associate"]["CA, LA"]]
    i = 0
    query_start = True
    company_id_loop = 0
    query = f"SELECT * FROM {table_name}"
    for column in columns:
        if column == "company_id":
            company_id_loop = company_id_loop + 1
        
        blank_field = False
        search_list = search_lists[i]
        if i == 0 or query_start == True:
            j = 0
            for search_item in search_list:
                if len(search_list) == 0:
                    query_start = True
                    blank_field = True
                    break

                if len(search_list) == 1:
                    if search_list[0] == "":
                        query_start = True
                        blank_field = True
                        break

                if j == 0:
                    if column == "company_id" and company_id_loop <= 1:
                        query = query + f" \nWHERE ({column} = (SELECT {column} FROM companies WHERE company_name = '{search_item}')"
                        query_start = False
                    elif column == "company_id" and company_id_loop == 2:
                        full_name = search_item.split()
                        query = query + f" \nWHERE ({column} = (SELECT {column} FROM connections WHERE first_name = '{full_name[0]}' AND last_name = '{full_name[1]}')"
                        query_start = False

                    else:
                        query = query + f" \nWHERE ({column} LIKE '%{search_item}%'"
                        query_start = False
                    j = j + 1
                else:
                    if column == "company_id" and company_id_loop <= 1:
                        query = query + f"\nOR {column} = (SELECT {column} FROM companies WHERE company_name = '{search_item}')"
                    elif column == "company_id" and company_id_loop == 2:
                        full_name = search_item.split()
                        query = query + f"\nOR {column} = (SELECT {column} FROM connections WHERE first_name = '{full_name[0]}' AND last_name = '{full_name[1]}')"

                    else:
                        query = query + f" \nOR {column} LIKE '%{search_item}%'"
                        query_start = False
            if len(search_list) > 0:
                if blank_field == False:
                    if column == "company_id" and company_id_loop != 2:
                        query = query + ")"
                    else:
                        query = query + ")"
            i = i + 1
        else:
            j = 0
            for search_item in search_list:
                if len(search_list) == 1:
                    if search_list[0] == "":
                        blank_field = True
                        break
                if j == 0:
                    if column == "company_id" and company_id_loop <= 1:
                        query = query + f" \nAND ({column} = (SELECT {column} FROM companies WHERE company_name = '{search_item}')"
                    elif column == "company_id" and company_id_loop == 2:
                        full_name = search_item.split()
                        query = query + f" \nAND ({column} = (SELECT {column} FROM connections WHERE first_name = '{full_name[0]}' AND last_name = '{full_name[1]}')"

                    else:
                        query = query + f" \nAND ({column} LIKE '%{search_item}%'"
                    j = j + 1
                else:
                    if column == "company_id" and company_id_loop <= 1:
                        query = query + f" \nOR {column} = (SELECT {column} FROM companies WHERE company_name = '{search_item}')"
                    elif column == "company_id" and company_id_loop == 2:
                        full_name = search_item.split()
                        query = query + f" \nOR {column} = (SELECT {column} FROM connections WHERE first_name = '{full_name[0]}' AND last_name = '{full_name[1]}')"

                    else:
                        query = query + f" \nOR {column} LIKE '%{search_item}%'"
            if len(search_list) > 0:
                if blank_field == False:
                    if column == "company_id" and company_id_loop != 2:
                        query = query + ")"
                    else:
                        query = query + ")"
            i = i + 1
    #print("ORDER BY IS: ", order_by)
    if order_by != "":
        query = query + f"\nORDER BY {order_by}"

    return query

#mysql modify query
def modify_query(sql):
    mycursor.execute(sql)
    mydb.commit()

@st.cache
def get_data(dataframe):
    data = dataframe
    return data

def combine_names(first_names, last_names):
    combined_list = []
    i = 0
    for i in range(len(first_names)):
        combined_list.append(str(first_names[i]) + " " + str(last_names[i]))
        i = i + 1
    return combined_list

def save_job(row):
    notes = st.text_input(f"Enter notes for job {row['job_id']}")
    save_job = st.button(f"Save job {row['job_id']}")
    if save_job:
        query = f"INSERT INTO saved_jobs(job_id, notes) VALUES ({row['job_id']}, '{notes}')"
        modify_query(query)

def show_jobs(my_data, show):
    if show:
        basic.subheader("RESULTS")
        for index, row in my_data.iterrows():
            with basic.expander(label = f"{row['job_title']} | {company_name_from_id(row['company_id'])} | {row['job_location']}"):
                st.write(f"**COMPANY: {company_name_from_id(row['company_id'])} | LEVEL: {row['job_level']} | TYPE: {row['job_type']}**")
                job_description = row['job_description'].replace('||','\n')
                job_description = job_description.replace('|','\n')
                url = row['job_link']
                st.write("[Full link](%s)" % url)
                save_job(row)

#THE APP--------------------------

#ELEMENTS---

#page title
st.title('LinkedIn Database Solutions')

#creating side bar
sb = st.sidebar

#Job Postings Sidebar Section
def job_postings_section():
    #st.header("What are you looking to find?")
    with st.expander(label = "Job Postings"):
        st.write("Job postings")
        #Title Search (matching titles) --> this is a list
        job_title_search = st.multiselect("Search by job title(s)", options = column_to_list("jobs", "job_title",0))
        #Company Search
        companies = column_to_list("companies", "company_name",0)
        if ['None'] in companies:
            companies.remove('None')
        job_company_search = st.multiselect("Search by company(s)", options = companies)
        #Location Search
        job_location_search = st.multiselect("Search by location(s)", options = column_to_list("jobs", "job_location",0))
        #Keyword search (look in description)
        job_keywords_search = st.text_input("Search by keyword(s)")
        job_keywords_search = job_keywords_search.split(",")
        clean_keywords_search = []
        for keyword in job_keywords_search:
            clean_keywords_search.append(keyword.strip())

        first_name_list = column_to_list("connections", "first_name",1)
        last_name_list = column_to_list("connections", "last_name",1)
        full_name_list = combine_names(first_name_list, last_name_list)
        connection_names = st.multiselect("Search jobs by connection(s)", options = full_name_list)
        first_names = []
        last_names = []
        for name in connection_names:
            name = name.split()
            first_names.append(name[0])
            last_names.append(name[1])

        #ORDER BY
        order_by = st.selectbox("Order by", options = ['Title', 'Location'])
        if order_by == 'Title':
            order_by = "job_title"
        elif order_by == 'Location':
            order_by = "job_location"
        else:
            order_by = ""
        
        #Apply filters button
        apply_filters_button = st.button("Apply Job Filters")

        #load state is false on first run through but once the button is clicked it goes to true
        if apply_filters_button or st.session_state.jobs_showing:
            st.session_state.jobs_showing = True
            print("JOBS ARE SHOWING")
            #st.write("APPLYING THE JOB FILTERS!")
            basic.header("Here are the jobs that meet the filters")
            sql = query_creator("jobs", ["job_title", "job_description", "job_location", "company_id", "company_id"],[job_title_search,clean_keywords_search,job_location_search, job_company_search, connection_names], order_by)
            basic.subheader("SQL QUERY")
            basic.text(sql)
            my_data = get_data(select_query(sql))

            converted_df = my_data.to_csv().encode('utf-8')
            
            basic.download_button("Download filtered job results", data = converted_df, file_name = "filtered_jobs.csv")

            print(my_data.shape)

            show_jobs(my_data, st.session_state.jobs_showing)

#My connections Sidebar Section
def my_connections_section():
    with st.expander(label = "My Connections"):
        st.write("My Connections")
        #Title Search (matching titles)
        first_name_list = column_to_list("connections", "first_name",1)
        last_name_list = column_to_list("connections", "last_name",1)
        full_name_list = combine_names(first_name_list, last_name_list)
        connection_names = st.multiselect("Search by name(s)", options = full_name_list)
        first_names = []
        last_names = []
        for name in connection_names:
            name = name.split()
            first_names.append(name[0])
            last_names.append(name[1])

        connection_companies = st.multiselect("Search connections by company(s)", options = column_to_list("companies", "company_name",0))
        
        connection_positions = st.multiselect("Search connections by position(s)", options = column_to_list("connections", "position",0))

        #ORDER BY
        connections_order_by = st.selectbox("Order by", options = ['First Name', 'Last Name', 'Position'])
        if connections_order_by == 'First Name':
            connections_order_by = "first_name"
        elif connections_order_by == 'Last Name':
            connections_order_by = "last_name"
        elif connections_order_by == 'Position':
            connections_order_by = "position"
        else:
            connections_order_by = ""
        

        #Apply filters button
        apply_connections_filters_button = st.button("Apply Connection Filters")
        #st.session_state.load_state = False #--> save jobs doesnt work
        # or st.session_state.load_state
        if apply_connections_filters_button:
            st.session_state.jobs_showing = False #--> have to press twice to display
            print("SETTING JOBS SHOWING TO FALSE")
            print("PRESSING CONNECTIONS BUTTON")
            #st.session_state.connections_showing = True
            print("CONNECTIONS ARE SHOWING")
            st.write("APPLYING THE CONNECTIONS FILTERS!")
            basic.header("Here are the connections that meet the filters")
            sql = query_creator("connections", ["first_name","last_name", "company_id", "position"], [first_names,last_names, connection_companies,connection_positions], connections_order_by)
            basic.subheader("SQL QUERY")
            basic.text(sql)
            my_data = get_data(select_query(sql))
            print(my_data.shape)

            converted_df = my_data.to_csv().encode('utf-8')
            basic.download_button("Download filtered connections results", data = converted_df, file_name = "filtered_connections.csv")


            basic.subheader("RESULTS")
            for index, row in my_data.iterrows():
                with basic.expander(label = f"{row['first_name']} {row['last_name']}"):
                    first_name = row['first_name']
                    last_name = row['last_name']
                    st.write(f"**{first_name} {last_name}**")
                    st.write(f"**Position:** {row['position']}")
                    st.write(f"**Company:** {company_name_from_id(row['company_ID'])}")

#Saved jobs Sidebar section
def saved_jobs_section():
    with st.expander(label = "My Saved Jobs"):
        st.write("Saved Jobs")
        saved_jobs = st.button("Show Saved Jobs")
        if saved_jobs or st.session_state.saved_jobs:
            st.session_state.saved_jobs = True
            st.session_state.jobs_showing = False #--> have to press twice to display
            basic.header("Here are your saved jobs")

            #Loop through all unique job ids
            job_id_df = get_data(select_query("SELECT job_id FROM saved_jobs"))
            print(job_id_df)
            job_id_list = job_id_df.job_id.values.tolist()
            job_id_set = set(job_id_list)
            print(job_id_set)

            unique_key = 0

            for job_id in job_id_set:
                #SQL QUERY TO GET JOB TITLE AND JOB COMPANY
                sql = f"""
                SELECT jobs.job_title, companies.company_name 
                FROM saved_jobs 
                INNER JOIN jobs ON saved_jobs.job_id = jobs.job_id 
                INNER JOIN companies ON jobs.company_id = companies.company_id 
                WHERE saved_jobs.job_id = {job_id}
                LIMIT 1
                """
                job_title_company_df = get_data(select_query(sql))
                print(job_title_company_df)

                job_title_list = job_title_company_df.job_title.values.tolist()
                job_company_list = job_title_company_df.company_name.values.tolist()

                job_notes_df = get_data(select_query(f"SELECT notes FROM saved_jobs WHERE job_id = {job_id}"))
                job_notes_list = job_notes_df.notes.values.tolist()
                print(job_notes_list)

                with basic.expander(label = f"{job_title_list[0]} | {job_company_list[0]}"):
                    st.write("**SQL QUERY to get Job Title and Company**")
                    st.text(sql)
                    st.write(f"**Notes:**")
                    for note in job_notes_list:
                        st.write(note)
                
                    sql_get_max_saved_job_id = "SELECT MAX(saved_job_id) AS highest_saved_job_id FROM saved_jobs"
                    max_saved_id = get_data(select_query(sql_get_max_saved_job_id)).highest_saved_job_id.values.tolist()[0]
                    print("MAX SAVED ID: ", max_saved_id+1)
                    
                    notes = st.text_input(f"Enter new note for this saved job - {job_title_list[0]} (Job #{job_id})")
                    print(notes)
                    save_note = st.button(f"Save note (Job #{job_id})")
                    unique_key = unique_key + 1
                    if save_note:
                        print("YOU MADE IT!")
                        query = f"INSERT INTO saved_jobs(job_id, notes) VALUES ('{job_id}', '{notes}')"
                        print(query)
                        modify_query(query)
                        print("Job saved with notes: ", notes)

                    remove_saved_job = st.button(f"Remove saved job (#{job_id})")
                    if remove_saved_job:
                        sql = f"DELETE FROM saved_jobs WHERE job_id = {job_id}"
                        modify_query(sql)
                        st.write("Job removed from saved jobs!")

#creating the main body container (header and info)
basic = st.container()

#MAIN-------------------------------------------------------
with sb:
    st.subheader("What are you looking for?")
    job_postings_section()
    my_connections_section()
    saved_jobs_section()
