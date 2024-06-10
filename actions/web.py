from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
import selenium.common.exceptions
from webdriver_manager.firefox import GeckoDriverManager
import tqdm

from llm import LLM


webLLM = LLM(model="accounts/fireworks/models/llama-v3-70b-instruct", 
             system_prompt="You are a helpful assistant that reads raw website text and responds with a human readable result based on a query.")

from .action import Action, Param

# interactable_elements = ["input", "button", "a", "select", "textarea", "iframe", "object", "embed", "area", "map", "audio", "video", "canvas", "details", "summary", "fieldset", "form", "label", "legend", "meter", "optgroup", "option", "output", "progress", "select", "textarea", "details", "summary", "menuitem", "menu", "command", "datalist", "keygen", "optgroup", "option", "select", "textarea", "button", "fieldset", "input", "label",]
clickable_elements = ["button", "a", "form", "menuitem", "menu"]
typable_elements = ["input", "textarea", "select"]

class FireWeb:
    NUM_CLASSES = 0
    def __init__(self):
        FireWeb.NUM_CLASSES += 1
        if FireWeb.NUM_CLASSES > 1:
            print("wtf")
            return
        self.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        
        self.clickable_elements = {}
        self.typeable_elements = {}
        self.website_text = {}
        self.most_recent_search_results = []

    def open_website(self, url):
        self.driver.get(url)

    def getURL(self):
        return self.driver.current_url

    def get_text_fast(self):
        return self.driver.find_element(By.XPATH, "/html/body").text

    def search_google(self, query):
        self.driver.get(f"https://www.google.com/search?q={query}")
        self.clickable_elements[f"https://www.google.com/search?q={query}"] = {}
        self.typeable_elements[f"https://www.google.com/search?q={query}"] = {}
        # get all search results
        search_results = self.driver.find_elements_by_css_selector("h3")
        results = []
        for result in search_results:
            if result.text.strip() == "": continue
            href = result.find_element_by_xpath("..").get_attribute("href")
            if not href: continue
            print("Found search result: " + result.text)
            self.clickable_elements[f"https://www.google.com/search?q={query}"][result.text] = result
            if href:
                results.append(href)
        self.website_text[f"https://www.google.com/search?q={query}"] = "Search results for " + query + ":\n" + "\n".join(results)
        self.most_recent_search_results = results
        return results

    def parse_elements(self, force_update=False):
        if self.getURL() in self.clickable_elements and not force_update: 
            return self.clickable_elements[self.getURL()], self.typeable_elements[self.getURL()], self.website_text[self.getURL()]
        self.typeable_elements[self.getURL()] = {}
        self.clickable_elements[self.getURL()] = {}
        self.website_text[self.getURL()] = self.driver.find_element_by_tag_name("body").text
        # ignore divs in xpath
        elements = self.driver.find_elements_by_xpath("/html/body//*[not(self::div)]")
        for element in tqdm.tqdm(elements, desc="Reading website...", unit="element", total=len(elements)):
            try:
                if element.is_displayed():
                    if element.tag_name in typable_elements:
                        #print("selected", element.tag_name, element.get_attribute("id"), element.get_attribute("class"), element.text)
                        if not element.text.strip():
                            self.typeable_elements[self.getURL()][element.get_attribute("class")] = element
                        else:
                            self.typeable_elements[self.getURL()][element.text] = element
                    if element.tag_name in clickable_elements:
                        #print("clicked", element.tag_name, element.get_attribute("id"), element.get_attribute("class"), element.text)
                        self.clickable_elements[self.getURL()][element.text] = element
                    
            except selenium.common.exceptions.StaleElementReferenceException:
                continue
        self.clickable_elements[self.getURL()]["go_to_prev_page"] = "PREV_PAGE"
        self.clickable_elements[self.getURL()]["go_to_next_page"] = "NEXT_PAGE"
        return self.clickable_elements[self.getURL()], self.typeable_elements[self.getURL()], self.website_text[self.getURL()] 
    
    def get_text(self):
        if not self.getURL() in self.website_text:
            self.parse_elements()
        return self.website_text[self.getURL()]
        
    def type_and_enter(self, element, text):
        if not self.getURL() in self.typeable_elements:
            self.parse_elements()
        if element in self.typeable_elements[self.getURL()]:
            self.typeable_elements[self.getURL()][element].send_keys(text)
            self.typeable_elements[self.getURL()][element].send_keys(webdriver.common.keys.Keys.RETURN)
        self.parse_elements()

    def click_element(self, element):
        if not self.getURL() in self.clickable_elements:
            self.parse_elements()
        if element in self.clickable_elements[self.getURL()]:
            if element == "go_to_prev_page":
                self.driver.back()
            elif element == "go_to_next_page":
                self.driver.forward()
            else:
                self.current_clickable_elements[element].click()
        self.parse_elements()

fireweb = FireWeb()

# @Action.action("open_website", 
#                "Open the website with the given URL.", 
#                [Param("url", "string", "URL of the website to open")],
#                requried_state="any", change_state="none")
# def open_website(url):
#     fireweb.open_website(url)
#     clickable_elements, typeable_elements, text = fireweb.parse_elements()
#     return f"You are now on the website: {fireweb.getURL()}. The text on this page is:\n###\n{text}\n###\n."

# @Action.action("type_text", 
#                "Type the given text in the element with the given name. The element must be a textbox or a textarea.", 
#                [Param("element", "string", enum_supplier=lambda: list(fireweb.parse_elements()[1].keys())), 
#                 Param("text", "string", "Text to type in the element")],
#                requried_state="any", change_state="none")
# def type_text(element, text):
#     fireweb.type_and_enter(element, text)
#     clickable_elements, typeable_elements, text = fireweb.parse_elements()
#     return f"You have just typed {text} in {element}. You are now on the website: {fireweb.getURL()}. The text on this page is:\n###\n{text}\n###\n."

@Action.action("enter_webbrowser",
                "Enter the web browser. From the web browser, you can search Google, click on search results, and read the text on the page of the search result.",
                [],
                requried_state="any", change_state="webbrowser")
def enter_webbrowser():
    return "You are now in the web browser. You can search Google, click on search results, and read the text on the page of the search result."

@Action.action("exit_webbrowser",
                "Exit the web browser.",
                [],
                requried_state="webbrowser read_search_result", change_state="none")
def exit_webbrowser():
    return "You have exited the web browser."

@Action.action("search_google", 
               "Search Google for the given query.", 
               [Param("query", "string", "Query to search Google for")],
               requried_state="webbrowser", change_state="google_search_results")
def search_google(query):
    results = fireweb.search_google(query)
    return f"Here are the results for your query, {query}. Use choose_search_result to click on one: " + ', '.join(results)

@Action.action("choose_search_result",
                "Choose the search result with the given name. It has the ability to click physically on the screen to open up the search result.",
                [Param("result", "string", "Name of the search result to choose", enum_supplier=lambda: fireweb.most_recent_search_results)],
                requried_state="google_search_results read_search_result", change_state="search_result")
def choose_search_result(result):
    fireweb.open_website(result)
    return f"You are now on the website: {fireweb.getURL()}."

@Action.action("read_text_on_page",
               "Read the text on the current page.",
               [Param("query", "string", "Query of what you want to find on the page. This will be used to generate a summary of the text on the page.")],
               requried_state="search_result", change_state="read_search_result")
def read_text_on_page(query):
    text = fireweb.get_text_fast()

    prompt = f"Here is the text on the page:\n\n###\n{text}\n###\n\nBased on this text write a summary based on this query: {query}"

    summary = webLLM.ask(prompt)

    return f"The text on the page {fireweb.getURL()} is:\n###\n{summary}\n###\n."

# @Action.action("click_element",
#                 "Click the element with the given name.",
#                 [Param("element", "string", enum_supplier=lambda: list(fireweb.parse_elements()[0].keys()))],
#                 requried_state="any", change_state="none")
# def click_element(element):
#     fireweb.click_element(element)
#     clickable_elements, typeable_elements, text = fireweb.parse_elements()
#     return f"You have just clicked {element}. You are now on the website: {fireweb.getURL()}. The text on this page is:\n###\n{text}\n###\n."