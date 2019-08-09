from libs.driverGetter import getDriver
from naver_cafe.parser.cafeBoardSearchParser import parse
import time
import json
from datetime import datetime
from selenium.webdriver.common.keys import Keys

driver = getDriver()

# driver.find_element_by_xpath('//*[@id="account"]/div/a').click()
# #
# #id
# driver.find_element_by_xpath('//*[@id="id"]').send_keys("")
# driver.find_element_by_xpath('//*[@id="pw"]').send_keys("")
# # login button
# driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()
# time.sleep(2)


def findKeywordDate(url, keyword, fromDate, toDate):
    keywordInput = driver.find_element_by_css_selector('#queryTop')
    keywordInput.clear()
    keywordInput.send_keys(keyword)

    #검색 버튼
    driver.find_element_by_xpath('//*[@id="main-area"]/div[1]/div[1]/form/div[4]/button').click()
    time.sleep(1)

    # list size 50
    driver.find_element_by_xpath('//*[@id="listSizeSelectDiv"]/a').click()
    driver.find_element_by_xpath('//*[@id="listSizeSelectDiv"]/ul/li[7]/a').click()

    # 검색기간 버튼 누르기
    driver.find_element_by_xpath('//*[@id="currentSearchDateTop"]').click()

    time.sleep(1)
    fromDateInputBox = driver.find_element_by_xpath('//*[@id="input_1_top"]')
    fromDateInputBox.clear()
    fromDateInputBox.send_keys(fromDate)
    fromDateInputBox.send_keys(Keys.TAB)

    time.sleep(1)

    toDateInputBox = driver.find_element_by_xpath('//*[@id="input_2_top"]')
    toDateInputBox.clear()
    toDateInputBox.send_keys(toDate)
    fromDateInputBox.send_keys(Keys.TAB)
    time.sleep(1)

    # 설정 버튼
    setupButton = driver.find_element_by_xpath('//*[@id="btn_set_top"]')
    setupButton.click()
    time.sleep(1)

    driver.find_element_by_xpath('//*[@id="main-area"]/div[1]/div[1]/form/div[4]/button').click()

    # paging button이 들어있는 박스
    prevNext = driver.find_element_by_xpath('//*[@id="main-area"]/div[7]')

    nextButton = None
    prevButton = None
    pagingItems = 0
    pagingItemCount = 0
    pageCount = 0
    divNodata = None
    # 마지막 페이지를 클릭한다
    try:
        nextButton = driver.find_element_by_css_selector('#main-area > div.prev-next > a.pgR > span')
    except:
        print("next button is None")

    try:
        pagingItems = prevNext.find_elements_by_tag_name("a")
    except:
        print("pagingItems is null")

    try:
        divNodata = driver.find_element_by_css_selector('document.querySelector("#main-area > div:nth-child(7) > table > tbody > tr > td > div")')
    except:
        divNodata = None
        print("divNodata is not exist")

    # item개수를 센다
    while nextButton != None:
        try:
            prevNext = driver.find_element_by_xpath('//*[@id="main-area"]/div[7]')
        except:
            prevNext = None
            print("prevNext is null")

        try:
            nextButton = driver.find_element_by_css_selector('#main-area > div.prev-next > a.pgR > span')
        except:
            nextButton = None
            print("next button is None")

        try:
            prevButton = driver.find_element_by_css_selector('#main-area > div.prev-next > a.pgL > span')
        except:
            prevButton = None
            print("prev button is None")

        try:
            pagingItems = prevNext.find_elements_by_tag_name("a")
            pagingItemCount = len(pagingItems)
        except:
            pagingItems = None
            pagingItemCount = 0
            print("pagingItems is null")

        try:
            divNodata = driver.find_element_by_css_selector('document.querySelector("#main-area > div:nth-child(7) > table > tbody > tr > td > div")')
        except:
            divNodata = None
            print("divNodata is not exist")

        print("isNextButton:{} isPrevButton:{} {}".format(nextButton != None, prevButton != None, pagingItemCount))

        # 다음은 있고 이전이 없고 개수가 11개 -> 첫 페이지 인데 500개 이상
        if(nextButton != None and prevButton == None and pagingItemCount == 11):
            print("첫 페이지 다음 버튼을 누른다")
            nextButton.click()
            pageCount += 1
        # 이전과 다음이 있고 개수가 12개
        elif(nextButton != None and prevButton != None and pagingItemCount == 12):
            print("nth page 다음 버튼을 누른다")
            nextButton.click()
            pageCount += 1
        time.sleep(1.5)

    # 다음이 없고 이전만 있고 개수가 11개 미만 -> 마지막 페이지
    if(nextButton == None and prevButton != None and pagingItemCount < 11):
        print("마지막 페이지에 가서 개수를 센다 pagingItemsCnt:{} pagingItems:{}".format(pageCount), pagingItemCount)
        # //*[@id="main-area"]/div[7]/a[1] <prev
        # //*[@id="main-area"]/div[7]/a[2]
        driver.find_element_by_xpath('//*[@id="main-area"]/div[7]/a[{}]'.format(pagingItemCount)).click()

    # 다음이 없고 이전도 없고 페이징도 0개
    elif (nextButton == None and prevButton == None and pagingItemCount == 0):
        print("검색 결과가 없음")
        pagingItemCount = 1
    # 다음이 없고 이전도 없고 개수가 10개 이하
    elif(nextButton == None and prevButton == None and pagingItemCount <= 10):
        print("검색결과가 첫페이지 마지막 페이지에 가서 개수를 센다 pagingItemsCnt:{} pagingItems:{}".format(pageCount, pagingItemCount))
        driver.find_element_by_xpath('//*[@id="main-area"]/div[7]/a[{}]'.format(pagingItemCount)).click()
    elif(nextButton == None and prevButton == None and pageCount == 0 and pagingItems == 12):
        pagingItemCount = 1
    else:
        print("--pageCount:{} pagingItems:{}-".format(pageCount, pagingItemCount))

    pageString = driver.page_source
    lastPageItemCount = parse(pageString)
    cafeName = url.split("clubid=")[1]
    print("pageCount:{} pagingItemCount:{} lastPageItemCount:{}", pageCount, pagingItemCount, lastPageItemCount)
    total = (pageCount * 10 * 50) + (pagingItemCount - 1) * 50 + (lastPageItemCount // 2)
    return {"cafeName": cafeName, "keyword":keyword, "fromDate":fromDate, "toDate":toDate, "total":total}



def getResultList(cafeUrl, keyword, dateList):
    resultList = []
    for date in dateList:
        print(cafeUrl, keyword, date)
        res = findKeywordDate(cafeUrl, keyword, date['fromDate'], date['toDate'])
        print(res)
        resultList.append(res)
        time.sleep(1)
    return resultList


keywordList = [
    "락토핏",
    "엘레나",
    "프로스랩",
    "아임비오",
    "자로우펨도피러스",
    "셀티아이",
    "여에스더",
    "애터미",
    "암웨이",
    "레이디스밸런스",
    "듀오락",
    "닥터아돌",
    "락피도",
    "드시모네"
]

dateList = [
    {"fromDate":"2018-01-01", "toDate":"2018-01-31"},
    {"fromDate":"2018-02-01", "toDate":"2018-02-28"},
    {"fromDate":"2018-03-01", "toDate":"2018-03-31"},
    {"fromDate":"2018-04-01", "toDate":"2018-04-30"},
    {"fromDate":"2018-05-01", "toDate":"2018-05-31"},
    {"fromDate":"2018-06-01", "toDate":"2018-06-30"},
    {"fromDate":"2018-07-01", "toDate":"2018-07-31"},
    {"fromDate":"2018-08-01", "toDate":"2018-08-31"},
    {"fromDate":"2018-09-01", "toDate":"2018-09-30"},
    {"fromDate":"2018-10-01", "toDate":"2018-10-31"},
    {"fromDate":"2018-11-01", "toDate":"2018-11-30"},
    {"fromDate":"2018-12-01", "toDate":"2018-12-31"},
    {"fromDate":"2019-01-01", "toDate":"2019-01-31"},
    {"fromDate":"2019-02-01", "toDate":"2019-02-28"},
    {"fromDate":"2019-03-01", "toDate":"2019-03-31"},
    {"fromDate":"2019-04-01", "toDate":"2019-04-30"},
    {"fromDate":"2019-05-01", "toDate":"2019-05-31"},
    {"fromDate":"2019-06-01", "toDate":"2019-06-30"},
    {"fromDate":"2019-07-01", "toDate":"2019-07-31"},
]

def collectKeywordCount(cafeUrl, fileName, keywordList, dateList):
    print(datetime.now())
    aa = []
    for keyword in keywordList:
        result = getResultList(cafeUrl, keyword, dateList)
        print(result)
        aa = aa + result

    print(datetime.now())

    file = open(fileName, "w+")
    file.write(json.dumps(aa))

cafeIdList = [
    {"id":"10298136", "cafeName":"remonterrace"},
    {"id":"10094499", "cafeName":"imsanbu"},
    {"id":"10080092", "cafeName":"esyori"},
    {"id":"10298136", "cafeName":"remonterrace"},
    {"id":"10298136", "cafeName":"remonterrace"},
    {"id":"10298136", "cafeName":"remonterrace"},
    {"id":"10298136", "cafeName":"remonterrace"},
    {"id":"10298136", "cafeName":"remonterrace"},
    {"id":"10298136", "cafeName":"remonterrace"},
]

idx = 0
url = 'https://cafe.naver.com/ArticleSearchList.nhn?search.clubid={}'.format(cafeIdList[idx]['id'])
driver.get(url)
driver.switch_to_frame("cafe_main")
collectKeywordCount(url, "./{}.json".format(cafeIdList[idx]['cafeName']), keywordList, dateList)

time.sleep(30)
driver.close()
