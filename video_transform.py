import tkinter
from tkinter.filedialog import askopenfile
from tkinter import messagebox
import cv2
import numpy as np
import math
import PIL
from PIL import Image, ImageTk
import time


class MainWindow(tkinter.Frame): # MainWindow наследник класса Frame

    def __init__(self, parent):

        super(MainWindow, self).__init__(parent)#вызов конструктора базового класса
        self.parent = parent #родитель – объект приложения
        #растянуть фрейм по размерам окна
        self.pack(fill=tkinter.BOTH,expand=1)


        self.cap = cv2.VideoCapture()
        #canvasi

        self.Canv1= tkinter.Canvas (self)
        self.Canv2= tkinter.Canvas (self)
        self.Canv3= tkinter.Canvas (self)
        self.Canv4= tkinter.Canvas (self)
        # привязка события изменения размера канваса к функции win_resize
        self.Canv1.bind("<Configure>",self.win_resize) 
        # параметры
        self.Frame = int(20)    #
        self.Skos = float(0.5)  #
        self.NCH_mask = int(1)  #
        self.Razm_mask = int(1) #
        self.ret = bool(0)      #
        self.img = np.ndarray(shape=(2,2))#
        # ползунки
        self.S1 = tkinter.Scale(self, from_=0, to=179, resolution=1 ,orient=tkinter.HORIZONTAL,command = self.change_S1 )# точка скоса
        self.S1.set(0)
        self.S2 = tkinter.Scale(self, from_=1, to=10, resolution=1 ,orient=tkinter.HORIZONTAL,command = self.change_S2)# размер маски нч фильтра
        self.S3 = tkinter.Scale(self, from_=1, to=10, resolution=1 ,orient=tkinter.HORIZONTAL,command = self.change_S3)# размер маски размытия
        self.SF = tkinter.Scale(self, from_=20, to=120, resolution=5,orient=tkinter.HORIZONTAL,command = self.change_SF)# частота кадров
        #растянуть сетку 5х9 по размерам фрейма
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_rowconfigure(8, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=0)
        #создать объекты виджетов 
        self.lb1=tkinter.Label(self, text = "скос")
        self.lb2=tkinter.Label(self, text = "нч фильтр")
        self.lb3=tkinter.Label(self, text = "размытие")
        self.lb4=tkinter.Label(self, text = "частота кадров ")
        self.lb5=tkinter.Label(self, text = "Номер камеры :")
        #textvariable
        self.paustr = tkinter.StringVar(value = "Пауза") # начальный текст кнопки паузы
        self.camstr = tkinter.StringVar(value = "Камера")# начальный текст кнопки считывания с камеры
        self.camnum = tkinter.StringVar(value = '1')# начальный номер камеры (н-1)
        #bool
        self.P_stat = bool(0)#счетчик нажатияна кнопку паузы
        self.C_stat = bool(0)#счетчик нажатия на кнопку считывания с камеры
        # entry
        self.Cam_entr = tkinter.Entry (self,textvariable = self.camnum) # поле для ввода номера камеры
        #командные кнопки 
        self.but_rv = tkinter.Button(self, text = "Видео",command=self.Read_video, height=1) # кнопка считывания видео
        self.but_rc = tkinter.Button(self, textvariable = self.camstr,command=self.Read_cam, height=1) # кнопка считывания с камеры
        self.but_ps = tkinter.Button(self, textvariable = self.paustr , command = self.Pause,height = 1)# кнопка паузы видео
        #разместить виджеты в сетке 5х9
        self.lb1.grid(row=1, column=4, sticky=tkinter.S)
        self.lb2.grid(row=3, column=4, sticky=tkinter.S)
        self.lb3.grid(row=5, column=4, sticky=tkinter.S)
        self.lb4.grid(row=7, column=4, sticky=tkinter.S)
        self.Canv1.grid(row = 1, column = 0 , columnspan= 2 , rowspan = 4, sticky=tkinter.NSEW)
        self.Canv2.grid(row = 1, column = 2,columnspan= 2 , rowspan = 4, sticky=tkinter.NSEW)
        self.Canv3.grid(row = 5, column = 0,columnspan= 2 , rowspan = 4, sticky=tkinter.NSEW)
        self.Canv4.grid(row = 5, column = 2, columnspan= 2 , rowspan = 4, sticky=tkinter.NSEW)
        self.but_rv.grid(row=0, column=0, sticky=tkinter.EW ,padx =20)
        self.but_rc.grid(row=0, column=1, sticky=tkinter.EW ,padx = 20)
        self.S1.grid(row = 2 , column = 4, sticky=tkinter.N)
        self.S2.grid(row = 4 , column = 4, sticky=tkinter.N)
        self.S3.grid(row = 6 , column = 4, sticky=tkinter.N)
        self.SF.grid(row = 8 , column = 4, sticky=tkinter.N)
        
    def __del__(self):
        
        if self.cap.isOpened():
            self.cap.release()
            
    def Pause(self) :
        
        if self.P_stat:
            self.P_stat = bool(0)
            self.paustr.set("Пауза")
            self.update(Sk=self.Skos,NC_m=self.NCH_mask,R_m=self.Razm_mask,Fr=self.Frame,index = 4)
        else:
            self.P_stat = bool(1)
            self.paustr.set("Пуск")
  
    def Read_video(self):
        
        if self.cap.isOpened(): 
            self.cap.release()
        f = askopenfile(mode='rb', defaultextension=".avi", filetypes=(("mp4 files", "*.mp4"),("awt files", "*.awt"),("avi files", "*.avi")))
        self.cap = cv2.VideoCapture(f.name)
        
        if self.cap.isOpened()==bool(0) : 
            messagebox.showerror("Data ERROR", "error while reading video")
            return
        #отображение кнопки паузы
        self.but_ps.grid(row = 0, column = 4)
        #запуск цикла обработки кадров
        self.update(float(self.Skos),int(self.NCH_mask),int(self.Razm_mask),int(self.Frame),int(4))
        
    def Read_cam(self):
        
        #при втором нажатии кнопки идет проверка является ли ид камеры числом
        if self.C_stat: 
            try:
                a = int(self.Cam_entr.get())
            except:
                messagebox.showerror("Data ERROR", "некорректный номер камеры")
        #скрытие поля ввода ид камеры
            else:                       
                self.lb5.grid_forget()  
                self.Cam_entr.grid_forget()
                self.camstr.set("Камера")
                self.C_stat = bool(0)
                a=a-1
        #проверка корректности ид камеры
                if (a<0):
                    a=0
                if self.cap.isOpened():
                    self.cap.release()
                self.cap = cv2.VideoCapture(a)
        
                if self.cap.isOpened()==bool(0) :
                    messagebox.showerror("Data ERROR", "error while reading video")
                    return
        #отображение кнопки паузы
                self.but_ps.grid(row = 0, column = 4)
        #запуск цикла обработки кадров
                self.update(float(self.Skos),int(self.NCH_mask),int(self.Razm_mask),int(self.Frame),int(4))
        #при первом нажатии на кнопку выводит поле ввода для ид камеры
        else:
            self.camstr.set("Пуск")
            self.lb5.grid(row=0, column=2, sticky=tkinter.E)
            self.Cam_entr.grid(row = 0, column = 3)
            self.C_stat = bool(1)
            
    #геометрическое преобразование скос   
    def Geometr_transform (self,image ,koef):
        
        rows, cols = image.shape[:2]
        src_points = np.float32([[0,0], [cols-1,0], [0,rows-1]])
        dst_points = np.float32([[0,0], [int(koef*(cols-1)),0], [int(float(1-koef)*(cols-1)),rows-1]])
        affine_matrix = cv2.getAffineTransform(src_points, dst_points)
        image = cv2.warpAffine(image, affine_matrix, (cols,rows))
        image = cv2.cvtColor(image , cv2.COLOR_BGR2RGB)
        return image
    
    #операция размытия
    def Operation (self,image,mask):
        
        kernel = np.ones((mask,mask), np.uint8)
        image = cv2.erode(image, kernel, iterations=1)
        image = cv2.cvtColor(image , cv2.COLOR_BGR2RGB)
        return image
    
    #применение нч фильтра
    def Filter (self , image , mask):
    
        kernel = np.ones((mask,mask), np.float32) / mask*mask
        image = cv2.filter2D(image, -1, kernel)
        image = cv2.cvtColor(image , cv2.COLOR_BGR2RGB)
        return image
    
    def update(self,Sk=float(0.5),NC_m=int(1),R_m=int(1),Fr=int(30),index=int(4)):
        
    #проверка видеозахвата
        if self.cap.isOpened():
    #после первого нажатия кнопки паузы следующий кадр не считывается а обновляется текущий
            if self.P_stat == bool(0):
                self.ret, self.img = self.cap.read()
    # изменение разрешения под размер канваса
            oh,ow,cn = self.img.shape
            oh,ow,cn = self.img.shape
            width = self.Canv1.winfo_width()
            height = self.Canv1.winfo_height()
            if (ow/oh>=width/height):
                height = int(width*(oh/ow))
            else:  
                width = int(height*(ow/oh))
            img = cv2.resize(self.img,(width,height))
            if self.ret:
    #вывод кадра со скосом
                if ((index == 4)or(index==1)):
                    Sk=float(1-(Sk/180))            #преобразование градусов скоса в десятичный коэф.
                    self.photo1 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.Geometr_transform(img,float(Sk))))
                    self.Canv1.delete("all")
                    self.Canv1.create_image(0, 0, image = self.photo1, anchor = tkinter.NW)
    #вывод кадра с нч фильтром
                if ((index == 4) or (index == 2)):
                    self.photo2 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.Filter(img , int(NC_m))))
                    self.Canv2.delete("all")
                    self.Canv2.create_image(0, 0, image = self.photo2, anchor = tkinter.NW)
    #вывод кадра с размытием
                if ((index == 4) or (index == 3)):
                    self.photo3 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.Operation(img,int(R_m))))
                    self.Canv3.delete("all")
                    self.Canv3.create_image(0, 0, image = self.photo3, anchor = tkinter.NW)
    #изменение пространства цветов кадра и его вывод              
                if (index == 4):
                    self.photo4 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(cv2.cvtColor(img , cv2.COLOR_BGR2XYZ)))
                    self.Canv4.delete("all")
                    self.Canv4.create_image(0, 0, image = self.photo4, anchor = tkinter.NW)
    #отложенный вызов функции обработки следующего кадра(при нажатой паузе не происходит) 
                if self.P_stat == bool(0):
                    application.after(int(1000/Fr), self.update,float(self.Skos),int(self.NCH_mask),int(self.Razm_mask),int(self.Frame),int(4))
    #при неудачной попытке считывания кадра(конец файла)
            else :
                self.but_ps.grid_forget()
                self.Canv1.delete("all")
                self.Canv2.delete("all")
                self.Canv3.delete("all")
                self.Canv4.delete("all")
                self.cap.release()
                
    #изменение значения точки скоса и обновление кадроа при нажатой паузе     
    def change_S1(self,a):
        
        self.Skos = a
        if self.P_stat == bool(1):
            self.update (Sk=self.Skos , index = 1)
            
    #изменение значения маски нч фильтра и обновление кадроа при нажатой паузе
    def change_S2(self,a):
        
        self.NCH_mask=a
        if self.P_stat == bool(1):
            self.update (NC_m = self.NCH_mask , index = 2)
            
    #изменение значения маски размытия и обновление кадроа при нажатой паузе
    def change_S3(self,a):
        
        self.Razm_mask=a
        if self.P_stat == bool(1):
            self.update (R_m = self.Razm_mask , index = 3)
            
    #изменение значения частоты кадров         
    def change_SF(self,a):
        
        self.Frame=a
        
    #изменение размера кадров при изменении размера окна на паузе       
    def win_resize(self,event):
        
        if self.P_stat==bool(1):
            self.update(Sk=self.Skos,NC_m=self.NCH_mask,R_m=self.Razm_mask,Fr=self.Frame,index = 4)
        
                
application = tkinter.Tk() #создание объекта приложения
application.minsize(500,500) # ограничение размера окна
window = MainWindow(application) #создание объекта основного окна
application.mainloop() #запуск цикла обработки сообщений системы
        

