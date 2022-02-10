---
title: gitlab-ci: 1.2.2 .gitlab-ci.yml 复杂示例 - 包含get gitlab tag message
date: 2020-06-11 11:50:00
categories: devops/git
tags: [devops,gitlab,git,ci,gitlab-runner]
---

### 0. 详细示例
此示例的软件基础：
- 自研公告API http://mynotify.com
- 自建gitlab http://mygitlab.com
- 自建awx（ansible tower开源版本） http://myawx.com

提前设定的gitlab project变量
- API_RESTART: true
- API_BUG: false
- API_ANNOUNCE: true
- API_ORGANIZER: dev
- 

``` yaml
deployapi:
  stage: deploy
  script:
    # 公告线上变更内容
    - MESSAGE=$(curl -H "PRIVATE-TOKEN:<my-private-token>" http://mygitlab.com/api/v4/projects/150/repository/tags/${CI_COMMIT_TAG}|jq -r '.message')
    - MESSAGE=$(echo "$MESSAGE"|sed 's/ \+/-/g')
    - msg='{"service_name":"api","is_restart":"'$API_RESTART'","is_bug":"'$API_BUG'","is_announce":"'$API_ANNOUNCE'","announce_message":"'$MESSAGE'","contacts":"'$GITLAB_USER_NAME'","organizer":"'$API_ORGANIZER'","build_user":"'$CI_JOB_ID'"}'
    - >
      curl -s -H "Content-Type: application/json" -H "token:mytoken" -X POST -d ${msg} http://mynotify.com/api/v1/jenkinsCount
    # 执行rsync，上线代码
    - echo ${RSYNC_PASS} > ./rsyncpass && chmod 600 ./rsyncpass
    - for ip in ${API_RSYNC_DEST_PART};
        do
          rsync -auvz --progress --no-o --no-g --no-p --delete
            --password-file=./rsyncpass
            --exclude="properties" --exclude="config.properties"
            --exclude="ftp.properties" --exclude="log4j.properties"
            ./api//target/api/* git@<ip>::api;
        done
    # 调用awx重启服务
    - data='{"extra_vars":{"role":"restart_tomcat_systemd_jenkins","host":"api","is_restart":"'$API_RESTART'"},"inventory":35}'
    - job_url=$(curl -X POST -H "Content-Type:application/json" -H "Authorization:Bearer <my-auth-string>" -d ${data} http://myawx.com/api/v2/job_templates/restart_tomcat_systemd_by_jenkins/launch/|jq -r '.url')
    # 检查重启job状态，对执行结果进行公告
    - status=""
    - while [ "$status" == "" ];
        do
          status=$(curl -H 'Content-Type:application/json' -H 'Authorization:Bearer <my-auth-string>' http://myawx.com${job_url}|jq -r '.status');
          [[ "${status}" == "pending" ]] && status="" && echo "job is pending" ;
          [[ "${status}" == "waiting" ]] && status="" && echo "job is waiting" ;
          [[ "${status}" == "running" ]] && status="" && echo "job is running" ;
          sleep 2;
        done
    - msg='{"service_name":"api-preferential","build_number":"'$CI_JOB_ID'"}'
    - if [ "$status" == "successful" ];
        then
          curl -X POST -H "Content-Type:application/json" -d ${msg}  http://mynotify.com/api/v1/jenkinsReply ;
        else
          echo "failed because status is ["$status"]"
          exit 1;
        fi
  only:
    - tags
  when: manual
```
整体的逻辑为：
- 公告线上变更内容
- 执行rsync上线代码
- 调用awx重启线上服务
- 检查awx job的状态，并将结果进行公告

yaml的注意点：
- curl POST的payload data字符串里面，不要有`空格`
- while和if这种多语句代码块，单独的命令后面要加上`;`，另外换行不需要`\`来转义，直接换行即可
- `[ "${var}" == "string" ]`判断逻辑中，变量要用`"`包裹

其他关键点：
- `curl http://domain.com|jq -r '.json字段'`，可以方便的通过api来获取自己想要的数据。例如，gitlab官方现在没有给tag的message内容提供内置变量，我只能手动来通过拥有read_api权限的token获取了。