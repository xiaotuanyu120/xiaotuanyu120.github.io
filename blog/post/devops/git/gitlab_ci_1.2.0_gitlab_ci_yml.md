---
title: gitlab-ci: 1.2.0 .gitlab-ci.yml
date: 2019-12-12 11:50:00
categories: devops/git
tags: [devops,gitlab,git,ci,gitlab-runner]
---
### gitlab-ci: 1.2.0 .gitlab-ci.yml example

---

### 0. .gitlab-ci.yml说明
参考链接：[.gitlab-ci.yml 官方文档](https://docs.gitlab.com/ee/ci/yaml/)
.gitlab-ci.yml是用于配置gitlab的pipeline，里面定义了
- gitlab-runner执行的内容
- 特定条件触发后任务的执行走向

``` yaml
image: <your-docker-image-repo>/sonarscanner:4.2

stages:
  - analysis

analysis:
  stage: analysis
  script:
  - cd /builds/<path-of-your-project>
  - wget https://repo1.maven.org/maven2/org/apache/tomcat/tomcat-jsp-api/7.0.96/tomcat-jsp-api-7.0.96.jar -O ./WebRoot/WEB-INF/lib/jsp-api.jar
  - wget https://repo1.maven.org/maven2/org/apache/tomcat/tomcat-servlet-api/7.0.96/tomcat-servlet-api-7.0.96.jar -O ./WebRoot/WEB-INF/lib/servlet-api.jar
  - echo > javafile.txt
  - find src/ -name *.java >> javafile.txt
  - jarfiles=()
  - for jar in $(find path/to/lib -name *.jar);do jarfiles=("${jarfiles[@]}" $jar);done
  - classfile=""
  - for cf in ${jarfiles[@]};do classfile="${classfile}:${cf}";done
  - /bin/mkdir -p path/to/classes
  - /usr/lib/jvm/java-1.7-openjdk/bin/javac -d path/to/classes -sourcepath src -cp $classfile @javafile.txt
  - /app/bin/sonar-scanner
    -Dsonar.host.url=http://sonarqube-domain:9000 
    -Dsonar.projectKey=project-name 
    -Dsonar.sources=./src 
    -Dsonar.sourceEncoding=UTF-8
    -Dsonar.java.binaries=./path/to/classes
    -Dsonar.java.libraries=./path/to/**/*.jar
  only:
  - master
```
> 注意点：
> - 只有一个stage里面的所有job都执行完毕了，才会去执行下一个stage
> - 同一个stage里面的job是同时被执行的
> - only限定了只有master分支commit后才会触发pipeline的执行