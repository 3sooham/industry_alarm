FROM oem0404/ubuntu_python:0.3

# ADD 복사할파일경로 이미지에서파일이위치할경로
ADD . /code/

RUN pip install -r /code/requirements.txt

RUN chown -R www-data:www-data /code

RUN ln -s /code/nginx-app.conf /etc/nginx/sites-enabled/
RUN ln -s /code/supervisor-app.conf /etc/supervisor/conf.d/

# WORKING DIRECTORY 변경
WORKDIR /code

# 외부 포트 포워딩을 도커 VM으로 연결하려면 도커 VM도 포트 노추랳줘야함
EXPOSE 80 22

# 해당 이미지를 컨테이너롤 띄울 때 디폴트로 실행할 커맨드나, ENTRYPOINT 명령문으로 지정된 커맨드에 디폴트로 넘길 파라미터를 지정할 때 사용
# 여기서는 supervisor 실행
CMD ["supervisord", "-n"]

