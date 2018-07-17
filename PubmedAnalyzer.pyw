import xml.etree.ElementTree as ET
import numpy as np
from operator import itemgetter
import xlsxwriter
from progress.bar import Bar
import sys
import os
import matplotlib.pyplot as plt
import datetime
from tkinter import *
import math


class PubmedAnalyzer:
	def  __init__(self,searchmode):
		if searchmode == 0:
			self.mesh = ""
			self.qualifier = ""
		elif searchmode == 1:
			self.mesh = "Parkinson Disease"
			self.qualifier = "immunology"
		elif searchmode == 2:
			self.mesh = "Parkinson Disease"
			self.qualifier = "genetics"
		
		self.localSource = os.path.dirname(os.path.abspath(__file__))+".\\pubmed_result.xml"
		self.localDest = os.path.dirname(os.path.abspath(__file__))+".\\results.xlsx"
		self.pubmed_matrix = []
		self.filteredBy = []
		self.articles = []
					

	def showBarChart(self):
		lastYear = ""
		year_vec = []
		for item in self.filteredBy: # <pmid,year>
			if item[4] == lastYear:
				year_vec.append(item)
			else:
				if year_vec != []:
					self.articles.append(year_vec)
				year_vec = []
				lastYear = str(item[4])
				year_vec.append(item)
			
		n_groups = len(self.articles)
		articles_foreach_year = []
		years = []
		for item in self.articles:
			articles_foreach_year.append(len(item))
			years.append(item[0][4]) # year of articles vector group
			
		fig, ax = plt.subplots()
		index = np.arange(n_groups)
		bar_width = 0.25
		opacity = 0.5
		err = 0.1
		error_config = {'ecolor': '0.3'}
		
		centerFactor = 32
		
		max_vec = []
		for item in self.articles:
			if len(item) > len(max_vec):
				max_vec = item
		
		rects = plt.bar(index, articles_foreach_year, bar_width,alpha=opacity,color='purple',yerr=err,error_kw=error_config,label="["+str(self.mesh)+","+str(self.qualifier)+"]")
		
		plt.xlabel('Years')
		plt.ylabel('Number Of Articles')
		plt.title('Articles Over Years')
		plt.xticks(index + bar_width/centerFactor,years,rotation=90)
		max = math.ceil(len(max_vec))+1
		if max <= 20: #visual threshold
			yint = range(0, math.ceil(len(max_vec))+1)
			plt.yticks(yint)
		
		plt.legend()
		plt.tight_layout()
		now = str(datetime.datetime.now().date())
		plt.savefig(os.path.dirname(os.path.abspath(__file__))+"\\_"+self.mesh.replace(" ", "").strip()+"_"+now.replace(" ", "").strip()+"_"+self.qualifier.replace(" ", "").strip()+".png",dpi=200,transparent=False)
		plt.show()
		
		

	
	def filterByPair(self):
		for item in self.pubmed_matrix:
			for j in range(5,len(item)):
				if str(item[j]) == self.mesh and str(item[j+1]) == self.qualifier:
					self.filteredBy.append(item) # <pmid,year>
					break
		self.filteredBy = sorted(self.filteredBy,key=itemgetter(4),reverse=True)
					

					
	def insertMatrixToCsv(self,pmid_ordered_matrix):
		workbook = xlsxwriter.Workbook(self.localDest)
		worksheet = workbook.add_worksheet('processed_data')
		row = 0
		col = 0
		for vec in pmid_ordered_matrix:
			col = 0
			for item in vec:
				worksheet.write(row,col,item)
				col+=1
			row+=1
		workbook.close()		

	
	def sortEachPmidSortedGroup(self):
		resultMat = []
		tmp_vec = []
		year = self.pubmed_matrix[0][4]
		for vector in self.pubmed_matrix:
			if vector[4] == year:
				tmp_vec.append(vector)
			else:
				year = vector[4]
				tmp_vec = sorted(tmp_vec,key=itemgetter(0),reverse=True) # sort by PMID
				for vec in tmp_vec:
					resultMat.append(vec)
				tmp_vec = [vector]
		self.pubmed_matrix = resultMat
		
		
	def xmlParsing(self):
		tree = ET.parse(self.localSource)
		root = tree.getroot()
		features = [] #[PMID,TITLE,SOURCE,AUTHOR,YEAR,M1,M2,M3,M4,M5,AMOUNT]
		for pa in root.findall('PubmedArticle'):
			for mc in pa.findall('MedlineCitation'):
				pmid = mc.find('PMID')
				try:
					features.append(str(pmid.text)) #PMID
				except:
					features.append("-")
				try:
					article = mc.find('Article')
				except:
					break
				try:
					journal = article.find('Journal')
					tt = journal.find('Title')
					features.append(str(tt.text)) #SOURCE
				except:
					features.append("-")
				try:
					art = article.find('ArticleTitle')
					features.append(str(art.text)) #TITLE
				except:
					features.append("-")
				try:
					atli = article.find('AuthorList')
					at = atli.find('Author') #one is enough as the requiments are
					lastname = at.find('LastName')
					forename = at.find('ForeName')
					nameRepr = lastname.text+"."+forename.text[:1]
					features.append(str(nameRepr)) #AUTHOR
				except:
					features.append("-")
				try:
					ada = article.find('ArticleDate')
					year = ada.find('Year')
					features.append(str(year.text)) #YEAR
					_YEAR_ = True
				except:
					try:
						journal = article.find('Journal')
						issues = journal.find('JournalIssue')
						date = issues.find('PubDate')
						year = date.find('Year')
						features.append(str(year.text)) #YEAR
						_YEAR_ = True
					except:
						try:
							journal = article.find('Journal')
							issues = journal.find('JournalIssue')
							date = issues.find('PubDate')
							textYear = date.find('MedlineDate')
							year = re.match(r'[1-2][0-9]{3}',str(textYear.text))
							features.append(str(year.group())) #YEAR
							_YEAR_ = True
						except:
							features.append("0") #DEFAULT CASE
						
				mp_counter = 0 #This counter is taking TOP-5 Major Point Of Article.
				for meshList in mc.findall('MeshHeadingList'):  #MP1-MP5 (pair with qualifiers)
					meshTerm = ""
					for meshHeading in meshList.findall('MeshHeading'):
						for des in meshHeading.findall('DescriptorName'):
							if des.attrib['MajorTopicYN'] == "Y" or des.attrib['MajorTopicYN'] == "N":
								meshTerm = str(des.text)
									
						for qual in meshHeading.findall('QualifierName'):
							if qual.attrib['MajorTopicYN'] == "Y":
								if meshTerm != "":
									features.append(meshTerm)
									features.append(str(qual.text))
						meshTerm = ""
						
				self.pubmed_matrix.append(features)
				features = []
		
		#self.initProgressBar()
		#self.progress_bar.next()
		self.pubmed_matrix = sorted(self.pubmed_matrix,key=itemgetter(4),reverse=True) # sort by YEAR
		self.sortEachPmidSortedGroup()
		self.insertMatrixToCsv(self.pubmed_matrix)
		
		self.filterByPair()
		self.showBarChart()
		#self.progress_bar.finish()		
		
if __name__ == "__main__":
	if len(sys.argv) == 1:
		sys.exit(1)
	input = -1
	try:
		input = int(sys.argv[1])
	except:
		sys.exit(-1)
	if input < 0 or input > 2:
		sys.exit(-2)
	analyzer = PubmedAnalyzer(input)
	analyzer.xmlParsing()
	