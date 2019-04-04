import wx
import wx.lib
import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import sys
engine = create_engine('postgresql://cslab:TacoSh%40ck@localhost:5432/dboverflow')
 
class SelectQuestions(wx.Frame):
    """
    Class used for creating frames other than the main one
    """
    def __init__(self, title, parent = None):
        # super(AllQuestions, self).__init__(*args, **kw)
        # wx.Frame.__init__(self, title=title)
        wx.Frame.__init__(self, parent=parent, title=title)
        self.InitUI()
    def InitUI(self):
        Selections = ['Unanswered','Top 10 Scoring Questions', 'View All']
        panel = wx.Panel(self)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.listbox = wx.ListBox(panel,style = wx.LB_MULTIPLE, choices = Selections)
        hbox.Add(self.listbox, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
        btnPanel = wx.Panel(panel)
        vbox = wx.BoxSizer(wx.VERTICAL)
        GoBtn = wx.Button(btnPanel, wx.ID_ANY, 'Go', size=(90, 30))


        self.Bind(wx.EVT_BUTTON, self.ViewQs, id=GoBtn.GetId())

        vbox.Add((-1, 20))
        vbox.Add(GoBtn)
        

        btnPanel.SetSizer(vbox)
        hbox.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT, 20)
        panel.SetSizer(hbox)

        self.SetTitle('Make Selections')
        self.Centre()
        

    def ViewQs(self, event):
        Filtered = self.listbox.GetSelections()
        # print(Filtered)
        WhatYouWant = ""
        # print(Filtered)
        if(0 in Filtered):
            WhatYouWant = "Select * FROM questions WHERE questions.id NOT IN (select questionid from answers);"
            a = ViewQuestions(title = "Unanswered Questions", Query = WhatYouWant)
            a.Show()
        if(1 in Filtered):
            WhatYouWant = "select questions.id, questions.question, questions.ownerid, questions.creationdate, (votecounts.upvote -votecounts.downvote) as Score from votecounts inner join questions on questions.id = votecounts.id order by Score desc limit 10;"
            a = ViewQuestions(title = "Top Scoring Questions", Query = WhatYouWant,columns = ["score"])
            a.Show()
        if(2 in Filtered):
            WhatYouWant = "select * FROM Questions;"
            a = ViewQuestions(title = "All Questions", Query = WhatYouWant)
            a.Show()
            
        # print(WhatYouWant)
        # print(MyQuery)
        #create_Query = 
        # a = ViewQuestions(title = "Viewing Qs", Columns= QueryColumns, Query = WhatYouWant)
        # a.Show()


class ViewQuestions(wx.Frame):
    def __init__(self, title, parent = None, Query = "", columns = []):
        # super(AllQuestions, self).__init__(*args, **kw)
        # wx.Frame.__init__(self, title=title)
        wx.Frame.__init__(self, parent=parent, title=title)
        panel = wx.Panel(self)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        columns1 = ["Creation Date", "Owner Id","Question",  "id"]
        for i in range(0,len(columns1)):
            columns.append(columns1[i])
        ReturnVal = pd.read_sql_query(Query , con = engine)
        # print(ReturnVal)
        ReturnVal = ReturnVal.values
        # Columns.append("Question ID")
        # print(ReturnVal)
        self.index = 0
        self.TheList = wx.ListCtrl(panel, size=(1000,300),
                         style=wx.LC_REPORT
                         |wx.BORDER_SUNKEN
                         )
        # index = self.list.InsertStringItem(sys.maxint, i[0]) 
        #  self.list.SetStringItem(index, 1, i[1]) 
        #  self.list.SetStringItem(index, 2, i[2])
        for i in range(0,len(columns)):
            self.TheList.InsertColumn(0, str(columns[i]))
         # line = "This is just a test"
        # self.TheList.InsertItem(self.index, line)
        for i in range(0,len(ReturnVal)):
            # index = self.TheList.InsertItem(TheList[i], ReturnVal[i][0])
            self.TheList.InsertItem(i, str(ReturnVal[i][0]))
            for j in range(1,len(ReturnVal[i])):
                self.TheList.SetItem(i, j, str(ReturnVal[i][j]))
        hbox.Add(self.TheList, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
        btnPanel = wx.Panel(panel)
        vbox = wx.BoxSizer(wx.VERTICAL)
        AnswerBtn = wx.Button(btnPanel, wx.ID_ANY, 'Answer Question', size=(100, 30))
        ViewAnswers = wx.Button(btnPanel, wx.ID_ANY, 'View Answers', size = (100,30))
        UpvoteBtn = wx.Button(btnPanel, wx.ID_ANY, "Upvote", size = (100,30))
        DownvoteBtn = wx.Button(btnPanel, wx.ID_ANY, "Downvote", size = (100,30))


        self.Bind(wx.EVT_BUTTON, self.AnswerQ, id=AnswerBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.ViewAnswer, id = ViewAnswers.GetId())
        self.Bind(wx.EVT_BUTTON, self.UpVote, id = UpvoteBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.DownVote, id = DownvoteBtn.GetId())
        vbox.Add((-1, 20))
        vbox.Add(AnswerBtn)
        vbox.Add(ViewAnswers)
        vbox.Add(UpvoteBtn)
        vbox.Add(DownvoteBtn)
        

        btnPanel.SetSizer(vbox)
        hbox.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT, 20)
        panel.SetSizer(hbox)

        self.SetTitle('Questions')
        self.Centre()
        # line = "This is just a test"
        # self.TheList.InsertItem(self.index, line)
    def AnswerQ(self, event):
        # print("Go ahead")
        # item = self.TheList.GetItem(itemId=row, col=col)
        choice = self.TheList.GetFirstSelected()
        item = self.TheList.GetItem(itemIdx = choice, col = 0)
        textChoice = item.GetText()
        Answer= wx.TextEntryDialog(None, 'Answer:')
        UserId = wx.TextEntryDialog(None, 'Id: ')
        if Answer.ShowModal() == wx.ID_OK:
            if UserId.ShowModal() == wx.ID_OK:
                FilledIn = Answer.GetValue()
                TheId = UserId.GetValue()
                df = pd.DataFrame(data = [(FilledIn, TheId, textChoice)], columns= ["answer", "ownerid", "questionid"])
                df.to_sql(name = "answers", con = engine,if_exists= "append", index= False)
            

    def ViewAnswer(self,event):
        # print("These be the answers")
        choice = self.TheList.GetFirstSelected()
        item = self.TheList.GetItem(itemIdx = choice, col = 0)
        textChoice = item.GetText()
        b = Answers(title = "Answers", questionId = textChoice)
        b.Show()
    def UpVote(self,event):
        DownId = wx.TextEntryDialog(None, 'Id:')
        if DownId.ShowModal() == wx.ID_OK:
            UserId = DownId.GetValue()
            choice = self.TheList.GetFirstSelected()
            item = self.TheList.GetItem(itemIdx = choice, col = 0)
            textChoice = item.GetText()
            df = pd.DataFrame(data = [(UserId, textChoice, True)], columns= ["userid", "questionid", "vote"])
            df.to_sql(name = "votes", con = engine,if_exists= "append", index= False)
    def DownVote(self, event):
        DownId = wx.TextEntryDialog(None, 'Id:')
        if DownId.ShowModal() == wx.ID_OK:
            UserId = DownId.GetValue()
            choice = self.TheList.GetFirstSelected()
            item = self.TheList.GetItem(itemIdx = choice, col = 0)
            textChoice = item.GetText()
            df = pd.DataFrame(data = [(UserId, textChoice, False)], columns= ["userid", "questionid", "vote"])
            df.to_sql(name = "votes", con = engine,if_exists= "append", index= False)
       
        # self.list_ctrl.InsertColumn(0, 'Subject')
        # self.list_ctrl.InsertColumn(1, 'Due')
        # self.list_ctrl.InsertColumn(2, 'Location', width=125)
 
# class AllQuestions(wx.Frame):
#     def __init__(self, title, parent = None):
#         # super(AllQuestions, self).__init__(*args, **kw)
#         # wx.Frame.__init__(self, title=title)
#         wx.Frame.__init__(self, parent=parent, title=title)
class Answers(wx.Frame): 
    def __init__(self, title, parent = None, questionId = 0):
        # super(AllQuestions, self).__init__(*args, **kw)
        # wx.Frame.__init__(self, title=title)
        Columns = ['id', 'answer', 'owner ID', 'question ID', 'Creation Date']
        wx.Frame.__init__(self, parent=parent, title=title)
        panel = wx.Panel(self) 
        box = wx.BoxSizer(wx.VERTICAL) 
        lbl = wx.StaticText(panel,-1,style = wx.ALIGN_CENTER)
        txt =  pd.read_sql_query(f"""SELECT question  FROM Questions where id = """ + questionId + """;""" , con = engine) 
        txt = txt.values 
        txt = str(txt[0])
        lbl.SetLabel(txt)
        self.AnswerList = wx.ListCtrl(panel, size=(1000,300),
                         style=wx.LC_REPORT
                         |wx.BORDER_SUNKEN
                         )
        for i in range(0,len(Columns)):
            self.AnswerList.InsertColumn(0, str(Columns[i]))
        answr = pd.read_sql_query(f"""SELECT *  FROM Answers where questionid = """ + questionId + """;""" , con = engine) 
        answr = answr.values
        for i in range(0,len(answr)):
            # index = self.TheList.InsertItem(TheList[i], ReturnVal[i][0])
            self.AnswerList.InsertItem(i, str(answr[i][0]))
            for j in range(1,len(answr[i])):
                self.AnswerList.SetItem(i, j, str(answr[i][j]))
        # print(answr)
class GoPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        btnPanel = wx.Panel(self)
        Go = wx.Button(btnPanel, label = 'Go', pos = (100,50))
        Go.Bind(wx.EVT_BUTTON, self.ViewQs)
    def ViewQs(self, event):
        print("going to show you these")
class OptionsPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        Selections = ['Question', 'QuestionId', 'Votes', 'Creation Date', 'Select All']
        Options =wx.ListBox(self, size = (200,150), style = wx.LB_MULTIPLE, choices = Selections)
        # btnPanel = wx.Panel(self)
        # Go = wx.Button(btnPanel, label = 'Go', pos = (100,50))
        # Go.Bind(wx.EVT_BUTTON, self.ViewQs)
    # def ViewQs(self, event):
    #     print("going to show you these")
class MyPanel(wx.Panel):
 
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
 
        ViewQ = wx.Button(self, label='View Questions',pos = (520,300), size = (500,100))
        ViewQ.Bind(wx.EVT_BUTTON, self.AllQuestions)
        self.frame_number = 1
        Ask = wx.Button(self, label='Ask a Question',pos = (10,300), size=(500, 100))
        Ask.Bind(wx.EVT_BUTTON, self.AskQuestion )
        FunFacts = wx.Button(self, label = 'Fun Facts', pos = (1030, 300), size = (500,100))
        FunFacts.Bind(wx.EVT_BUTTON, self. ViewFun)
       
    def ViewFun(self, event):
        cool = FunFacts()
        cool.Show()
    def AllQuestions(self, event):
        title = 'Questions'
        frame = SelectQuestions(title=title)
        frame.Show()
        
        
    def AskQuestion(parent=None, message='', default_value=''):
        Question = wx.TextEntryDialog(None, 'Ask a Question:')
        Id = wx.TextEntryDialog(None, 'Id: ')
        if Question.ShowModal() == wx.ID_OK:
            if Id.ShowModal() == wx.ID_OK:
                Asking = Question.GetValue()
                Identify = Id.GetValue()
                df = pd.DataFrame(data = [(Asking, Identify)], columns= ["question", "ownerid"])
                df.to_sql(name = "questions", con = engine,if_exists= "append", index= False)
                # df.to_sql(name = Questions, con = engine, index = False)

                #use sqlalchemy directly or make dataframe
        # a = pd.read_sql_query(f"""INSERT INTO Questions (question, ownerid) VALUES (question = """ + str(Asking) + """, ownerid = """ + str(Identify) + """;""" , con = engine)
            # pd.read_sql_query(f"""INSERT INTO questions(question, id)
            #                         VALUES(question = str(Asking), id = 5""", con = engine)
 
class FunFacts(wx.Frame):
     def __init__(self):
         wx.Frame.__init__(self, None, title = 'Fun Facts', size = (600,145))
         panel = wx.Panel(self)
         lbl = wx.StaticText(panel,-1)
         font = wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL) 
         a = pd.read_sql_query(f"""select (count(questions.ownerid) + count(answers.ownerid)) as total, users.name from questions inner join answers
          on questions.id = answers.questionid inner join users on questions.ownerid = users.id group by questions.ownerid, users.name order by total desc limit 1;""" , con = engine) 
         a = a.values
        #  print(a)
         ActiveUser = "Most Active User: " + str(a[0][1])
         
         b = pd.read_sql_query(f"""select count(creationdate::date) as CDate, creationdate from questions group by creationdate order by CDate desc limit 1;""" , con = engine)  
         b = b.values
         c = pd.read_sql_query(f"""select count(creationdate::date) as CDate, creationdate from answers group by creationdate order by CDate desc limit 1;""" , con = engine)
         c = c.values
        #  d = pd.read_sql_query(f"Select question FROM questions WHERE questions.id NOT IN (select questionid from answers) order by questions.id limit 1;", con = engine)
        #  d.values
        #  print(d.shape)
        #  longestUn = str(d)
        #  longestUn = "Longest Unanswered Question: " + longestUn
         PopAns = c[0][1].date()
         PopDateA = PopAns.strftime("%B - %d - %Y")
         PopDateA = "Date with most answers given: " + PopDateA
         PopDate = b[0][1].date()
         PopDateQ = PopDate.strftime("%B - %d - %Y")
         PopDateQ = """Date with most questions asked: """ + PopDateQ
         txt = ActiveUser + "\n" + PopDateQ + "\n" + PopDateA 
         lbl.SetFont(font)
         lbl.SetLabel(txt)
        #  print(PopDate)
        
         
         #most active user
        #  select questions.ownerid, (count(questions.ownerid) + count(answers.ownerid))
        #  as total from questions inner join answers on questions.id = answers.questionid group
        #  by questions.ownerid order by total desc limit 1;
class MainFrame(wx.Frame):
 
    def __init__(self):
        wx.Frame.__init__(self, None, title='Main Frame', size=(2080, 1800))
        panel = MyPanel(self)
        self.Show()
 
 
if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()