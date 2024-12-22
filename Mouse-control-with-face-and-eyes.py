
import cv2
import pyautogui as robot
import face_recognition as fr
import matplotlib.pyplot as plt

# تنظیمات دوربین
cam=cv2.VideoCapture(0)
_ ,img=cam.read()
cam.release


# وارد کردن هاردکست کیت
face_model=cv2.CascadeClassifier("f1.xml")
eye_model=cv2.CascadeClassifier("eyye.xml")

# تنظیم رنگ بندی تصویر
gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
face=face_model.detectMultiScale(gray)
eye=eye_model.detectMultiScale(gray)




loop = True
while loop:
    # باز کردن دوربین
    _, img=cam.read()
    img=cv2.flip(img,1)

    # تنظیمات رنگ
    red=0,0,250
    whait=250,250,250

    # مشخص کردن موقیت موس
    mous_x=robot.position().x
    mous_y=robot.position().y

    # تنظیم رنگ بندی تصویر
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # وارد کردن عکس سیاه سفید به متغیر
    face=face_model.detectMultiScale(gray)
    eye=eye_model.detectMultiScale(gray)

    # مشخص کردن موقیت صورت
    if (len(face))>0:
        x = face[0][0]
        y = face[0][1]
        x2= x + face[0][2]
        y2 = y+ face[0][3]
        gray_face = gray[y:y2:,x:x2]



        # مشخص کردن موقیت چشم
        eye=eye_model.detectMultiScale(gray_face,minSize=(30, 30),scaleFactor=1.1,minNeighbors=5)
        imgout=img.copy()

    # کشیدن رگتنگل دور صورت
    out=cv2.rectangle(img,(x,y),(x2,y2),(250,0,0),3)

    rang=whait

    # حرکت موس به سمت چپ و  راست  و بالا و پایین
    if x<135:
        rang=red
        mous_x=mous_x - abs(x-135)
        robot.moveTo(mous_x,mous_y,0)

    if x2>390:
        rang=red
        mous_x=mous_x + abs(x-390)
        robot.moveTo(mous_x,mous_y,0)


    
    if y<150:
        rang=red
        mous_y=mous_y + abs(y-150)
        robot.moveTo(mous_x,mous_y,0)
    
    if y2>400:
        rang=red
        mous_y=mous_y + abs(y2-400)
        robot.moveTo(mous_x,mous_y,0)
    # خط مرز حرکت صورت
    out=cv2.rectangle(img,(135,150),(390,400),rang,3)

    # پخش کردن موقیت ها بین  متغیر ها
    ic=0
    for (xe, ye, w, h) in eye:
        ic=ic+1

        # کشیدن علامت چشم
        cv2.rectangle(img, (xe+x,ye+y), (xe+w+x,ye+h+y), (250,50,250),3)
        if ic==2:
            break
    # کلیک کردن موس با حرکت چشم
    if xe>105:
        robot.click(mous_x, mous_y)

    # بستن دوربین
    cv2.imshow('nicot',out)
    if cv2.waitKey(1) == ord('q'):
        loop=False
        cv2.destroyAllWindows()
        cam.release
        break
    
    
    
            
        

    