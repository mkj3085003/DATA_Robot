import cv2
import numpy as np
import imutils
from imutils import contours
import myutils


# def cv_show(name,img):
# 	cv2.imshow(name, img)
# 	cv2.waitKey(0)
# 	cv2.destroyAllWindows()

class ReadNumber:
    def __init__(self) -> None:

        self.number = 100
        self.digits = {}
        self.binary_image=()

    def get_template(self):
        img = cv2.imread("C:\\Users\\12245\\Documents\\Unreal Projects\\HarixSim2\\python\\DATA_Robot\\VLM_container\\number.png")
        ref = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 二值图像
        ref = cv2.threshold(ref, 10, 255, cv2.THRESH_BINARY_INV)[1]
        #返回的list中每个元素都是图像中的一个轮廓
        refCnts, _ = cv2.findContours(ref.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(img,refCnts,-1,(0,0,255),3)
        refCnts = imutils.contours.sort_contours(refCnts, method="left-to-right")[0]
        for (i, c) in enumerate(refCnts):
        # 计算外接矩形并且resize成合适大小
            (x, y, w, h) = cv2.boundingRect(c)
            roi = ref[y:y + h, x:x + w]
            roi = cv2.resize(roi, (57, 88))
            self.digits[i] = roi
        return  self.digits

    def preprocess_image(self,img):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # cv_show('gray',gray)
        cv2.imwrite("C:\\Users\\12245\\Documents\\Unreal Projects\\HarixSim2\\python\\DATA_Robot\\VLM_container\\gray_instance.png",gray)

        x1, y1 = 751, 200
        x2, y2 = 804, 237
        # 通过切片操作进行图像裁剪,抠出空调板
        cropped_image = gray[y1:y2, x1:x2]
        self.binary_image = cv2.threshold(cropped_image, 125, 150, cv2.THRESH_BINARY_INV)[1]
        return self.binary_image

    def detect_digits(self):
        rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
        sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))

        gradX = cv2.Sobel(self.binary_image, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
        gradX = np.absolute(gradX)
        gradX = (255 * ((gradX - np.min(gradX)) / (np.max(gradX) - np.min(gradX)))).astype("uint8")

        gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKernel)
        thresh = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, sqKernel)

        threshCnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = threshCnts
        locs = []

        for (i, c) in enumerate(cnts):
            (x, y, w, h) = cv2.boundingRect(c)
            if (w > 40) and (h > 10):
                locs.append((x, y, w, h))

        locs = sorted(locs, key=lambda x: x[0])
        output = []

        for (i, (gX, gY, gW, gH)) in enumerate(locs):
            groupOutput = []
            group = self.binary_image[gY:gY + gH, gX:gX + gW]
            group = cv2.threshold(group, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

            digitCnts, hierarchy = cv2.findContours(group.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            digitCnts = contours.sort_contours(digitCnts, method="left-to-right")[0]

            for c in digitCnts:
                (x, y, w, h) = cv2.boundingRect(c)
                roi = group[y:y + h, x:x + w]
                roi = cv2.resize(roi, (55, 87))

                scores = []
                for (digit, digitROI) in self.digits.items():
                    result = cv2.matchTemplate(roi, digitROI, cv2.TM_CCOEFF)
                    (_, score, _, _) = cv2.minMaxLoc(result)
                    scores.append(score)

                groupOutput.append(str(np.argmax(scores)))
                # print(groupOutput)

            cv2.rectangle(self.binary_image, (gX - 5, gY - 5), (gX + gW + 5, gY + gH + 5), (0, 0, 255), 1)
            cv2.putText(self.binary_image, "".join(groupOutput), (gX, gY - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
            output.extend(groupOutput)
            # print("output-numper:",output)
            number_str = ''.join(output)  # 将列表中的字符串元素连接起来
            self.number = int(number_str)  # 将结果字符串转换为整数
            print("---I see air condition 's temprature: ",self.number,"℃---")
            return self.number



