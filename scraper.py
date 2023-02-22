#import libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

#------------------------SCRAPER FUNCTION------------------------
def linkedinScraper(urls, csv_name, num_jobs_per_page, job_type_descriptions):

    for job_page in range(len(urls)):
        # Creating a webdriver instance
        driver = webdriver.Chrome("ChromeDriver_Path/chromedriver")
        
        # Opening the url we have just defined in our browser
        driver.get(urls[job_page])

        #We create a while loop to browse jobs. 
        i = 0
        #change back to 50
        while i <= 5:
            print("I: ", i)
            #We keep scrollind down to the end of the view.
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            i = i + 1
            try:
                #We try to click on the load more results buttons in case it is already displayed.        
                infinite_scroller_button = driver.find_element(By.XPATH, ".//button[@aria-label='Load more results']")
                driver.execute_script("arguments[0].click();", infinite_scroller_button)
            #infinite_scroller_button.click()
                time.sleep(1)
            except:
                #If there is no button, there will be an error, so we keep scrolling down.
                print("NO BUTTON UH OH!")
                time.sleep(0.1)
                pass


        #We get a list containing all jobs that we have found.
        job_lists = driver.find_element(By.CLASS_NAME,"jobs-search__results-list")
        jobs = job_lists.find_elements(By.TAG_NAME,"li") # return a list

        #We declare void list to keep track of all obtaind data.
        job_title_list = []
        company_name_list = []
        location_list = []
        date_list = []
        job_link_list = []

        #We loof over every job and obtain all the wanted info.
        #for job in jobs:
        i = 0
        for job in jobs:
            #loop through however many jobs - up to 900 - might be able to delete this if
            if i == num_jobs_per_page:
                break
            #job_title
            job_title = job.find_element(By.CSS_SELECTOR,"h3").get_attribute("innerText").strip()
            job_title_list.append(job_title)
            
            #company_name
            company_name = job.find_element(By.CSS_SELECTOR,"h4").get_attribute("innerText").strip().replace('\n','|')
            company_name_list.append(company_name)
            
            #location
            location = job.find_element(By.CSS_SELECTOR,"div>div>span").get_attribute("innerText").strip().replace('\n','|')
            location_list.append(location)
            
            #date
            date = job.find_element(By.CSS_SELECTOR,"div>div>time").get_attribute("datetime").strip().replace('\n','|')
            date_list.append(date)
            
            #job_link
            job_link = job.find_element(By.CSS_SELECTOR,"a").get_attribute("href").strip().replace('\n','|')
            job_link_list.append(job_link)

            time.sleep(.1)
            i = i + 1

        print(job_title_list)
        print(len(job_title_list))

        jd = [] #job_description
        seniority = []
        emp_type = []
        job_func = []
        job_ind = []
        #for item in range(len(jobs)):
        for item in range(num_jobs_per_page):
            print(item)
            job_func0=[]
            industries0=[]
            # clicking job to view job details
            
            #__________________________________________________________________________ JOB Link
            #
            try:
                list_item = item+1
                job_click_path_button = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/section[2]/ul/li[' + str(list_item) + ']/div/a')
                driver.execute_script("arguments[0].click();", job_click_path_button)
                time.sleep(5)
            except:
                print("JOB CLICK DID NOT WORK!")
                pass

            #__________________________________________________________________________ JOB Description
            jd_path = '/html/body/div/div/section/div/div/section/div/div/section/div'
            try:
                jd0 = job.find_element(By.XPATH,jd_path).get_attribute('innerText').strip().replace('\n','|')
                jd.append(jd0)
            except:
                jd.append(None)
                pass
            
            #__________________________________________________________________________ JOB Seniority
            seniority_path='/html/body/div/div/section/div/div/section/div/ul/li[1]/span'
            
            try:
                seniority0 = job.find_element(By.XPATH,seniority_path).get_attribute('innerText').strip().replace('\n','|')
                seniority.append(seniority0)
            except:
                seniority.append(None)
                pass

            #__________________________________________________________________________ JOB Time
            emp_type_path='/html/body/div/div/section/div/div/section/div/ul/li[2]/span'
            
            try:
                emp_type0 = job.find_element(By.XPATH,emp_type_path).get_attribute('innerText').strip().replace('\n','|')
                emp_type.append(emp_type0)
            except:
                emp_type.append(None)
                pass
            
            #__________________________________________________________________________ JOB Function
            function_path='/html/body/div/div/section/div/div/section/div/ul/li[3]/span'
            
            try:
                func0 = job.find_element(By.XPATH,function_path).get_attribute('innerText').strip().replace('\n','|')
                job_func.append(func0)
            except:
                job_func.append(None)
                pass

            #__________________________________________________________________________ JOB Industry
            industry_path='/html/body/div/div/section/div/div/section/div/ul/li[4]/span'
            
            try:
                ind0 = job.find_element(By.XPATH,industry_path).get_attribute('innerText').strip().replace('\n','|')
                job_ind.append(ind0)
            except:
                job_ind.append(None)
                pass
            
            print("Current at: ", item, "Percentage at: ", (item+1)/num_jobs_per_page*100, "%")

        job_data = pd.DataFrame({
            'Date': date_list,
            'Company': company_name_list,
            'Title': job_title_list,
            'Location': location_list,
            'Description': jd,
            'Level': seniority,
            'Type': emp_type,
            'Function': job_func,
            'Industry': job_ind,
            'Link': job_link_list,
            'search_field': job_type_descriptions[job_page]
        })

        print(job_data.head())

        # append data frame to CSV file
        if job_page == 0:
            job_data.to_csv(csv_name + '.csv', mode='a', index=False, header=True)
        else:
            job_data.to_csv(csv_name + '.csv', mode='a', index=False, header=False)

        
        # print message
        print("Data appended successfully at loop " + str(i))

        #job_data.to_csv(csv_name + '.csv')
#------------------------END SCRAPER FUNCTION------------------------


#-------------------------MAIN---------------------------------
# url = input("\nEnter the linkedin url for the job page you would like to scrape: ")
#urls = ["https://www.linkedin.com/jobs/search/?currentJobId=3362755547&distance=25&geoId=103644278&keywords=data%20science", "https://www.linkedin.com/jobs/search?keywords=Data%20Analyst&location=United%20States&geoId=103644278&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"]
job_type_descriptions = ['Information and Technology', 'Agriculture', 'Film', 'Healthcare', 'Banking and Finance']
#urls = ['https://www.linkedin.com/jobs/search/?currentJobId=3373257369&f_E=2&f_JT=F&f_WT=1&geoId=102095887&keywords=information%20and%20technology&location=California%2C%20United%20States&refresh=true', 'https://www.linkedin.com/jobs/search/?currentJobId=3120985607&f_E=2&f_JT=F&f_WT=1&geoId=102095887&keywords=agriculture&location=California%2C%20United%20States&refresh=true', 'https://www.linkedin.com/jobs/search/?currentJobId=3120985607&f_E=2&f_JT=F&f_WT=1&geoId=102095887&keywords=film&location=California%2C%20United%20States&refresh=true', ' https://www.linkedin.com/jobs/search/?currentJobId=3373013434&f_E=2&f_JT=F&f_WT=1&geoId=102095887&keywords=healthcare&location=California%2C%20United%20States&refresh=true', 'https://www.linkedin.com/jobs/search/?currentJobId=3120985607&f_E=2&f_JT=F&f_WT=1&geoId=102095887&keywords=banking%20and%20finance&location=California%2C%20United%20States&refresh=true']
csv_name = input("\nEnter the name for your data file (do not include .csv): ")
urls = [input("\nEnter the full link for the jobs you would like to scrape: ")]
num_jobs_per_page = 20
print()
linkedinScraper(urls, csv_name, num_jobs_per_page, job_type_descriptions)
#-------------------------END MAIN---------------------------------
