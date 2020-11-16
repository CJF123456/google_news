# 基于镜像基础
FROM python:3.7
# 设置代码文件夹工作目录 /app
WORKDIR /google_news
# 复制当前代码文件到容器中 /app
ADD . /google_news
# 安装所需的包
RUN pip3 install -r requirements.txt
# 修改时区
RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

ENV PATH=$PATH:/google_news
ENV PYTHONPATH /google_news
#######################
COPY . .

RUN bash -c 'mkdir -p /data/logs/'

CMD ["python3", "./task/cron_start_task.py"]
