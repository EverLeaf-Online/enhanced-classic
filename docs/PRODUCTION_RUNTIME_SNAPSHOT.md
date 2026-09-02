# EverLeaf Production Runtime Snapshot

Generated: 2026-08-31T03:41:52Z
Source release commit: b57a0461c99743407978b0201afdd755e430832a
Remote inspection exit status: 0

```text
=== host ===
everleaf-vnic
ubuntu
Linux everleaf-vnic 6.17.0-1020-oracle #20-Ubuntu SMP Sat Jul 25 00:52:17 UTC 2026 aarch64 aarch64 aarch64 GNU/Linux

=== disk ===
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        96G   23G   74G  24% /
/dev/sda1        96G   23G   74G  24% /

=== /opt/everleaf layout ===
/opt/everleaf/backups
/opt/everleaf/backups/server
/opt/everleaf/backups/web
/opt/everleaf/discord
/opt/everleaf/nx-rewards-test
/opt/everleaf/nx-rewards-test/.devcontainer
/opt/everleaf/nx-rewards-test/.github
/opt/everleaf/nx-rewards-test/.idea
/opt/everleaf/nx-rewards-test/.mvn
/opt/everleaf/nx-rewards-test/database
/opt/everleaf/nx-rewards-test/docs
/opt/everleaf/nx-rewards-test/handbook
/opt/everleaf/nx-rewards-test/scripts
/opt/everleaf/nx-rewards-test/src
/opt/everleaf/nx-rewards-test/target
/opt/everleaf/nx-rewards-test/tools
/opt/everleaf/nx-rewards-test/wz
/opt/everleaf/patches
/opt/everleaf/patches/downloads
/opt/everleaf/patches/files
/opt/everleaf/patches/files.old
/opt/everleaf/qa-agent-hub
/opt/everleaf/qa-agent-hub/.github
/opt/everleaf/qa-agent-hub/.idea
/opt/everleaf/qa-agent-hub/.mvn
/opt/everleaf/qa-agent-hub/build
/opt/everleaf/qa-agent-hub/database
/opt/everleaf/qa-agent-hub/deploy
/opt/everleaf/qa-agent-hub/docs
/opt/everleaf/qa-agent-hub/handbook
/opt/everleaf/qa-agent-hub/scripts
/opt/everleaf/qa-agent-hub/src
/opt/everleaf/qa-agent-hub/tools
/opt/everleaf/qa-agent-hub/web
/opt/everleaf/qa-agent-hub/wz
/opt/everleaf/qa-secrets
/opt/everleaf/releases
/opt/everleaf/releases/631d51d22fd8ba0a2da4e45a0ae8ebab7ad4e2ef
/opt/everleaf/releases/6fecd6fcb1810df6d92e5d787e838030ece6acba
/opt/everleaf/releases/9908d278ed7385b69fc1dd2abe1bee924b77c8ba
/opt/everleaf/releases/a5b5e41829abfc61d677758500b0dc6f252d3041
/opt/everleaf/releases/d3208973c9967845f2485169a9f59aa2dd0ce1c2
/opt/everleaf/releases/d6d30d03376694a39f9704f00f72b588c11cab1c
/opt/everleaf/releases/e5295ad29544e496b0141dce7ba2ab43507a311e
/opt/everleaf/releases/fa9178708974eaedba11cf4ec20326c2780521a9
/opt/everleaf/server
/opt/everleaf/server/.devcontainer
/opt/everleaf/server/.git
/opt/everleaf/server/.github
/opt/everleaf/server/.idea
/opt/everleaf/server/.mvn
/opt/everleaf/server/database
/opt/everleaf/server/docs
/opt/everleaf/server/handbook
/opt/everleaf/server/scripts
/opt/everleaf/server/src
/opt/everleaf/server/target
/opt/everleaf/server/tools
/opt/everleaf/server/wz
/opt/everleaf/web
/opt/everleaf/web.pre-gtop-20260829T215641Z
/opt/everleaf/web.pre-gtop-20260829T215641Z/data
/opt/everleaf/web.pre-gtop-20260829T215641Z/node_modules
/opt/everleaf/web.pre-gtop-20260829T215641Z/ops
/opt/everleaf/web.pre-gtop-20260829T215641Z/public
/opt/everleaf/web.pre-gtop-20260829T215641Z/scripts
/opt/everleaf/web.pre-gtop-20260829T215641Z/sql
/opt/everleaf/web.pre-gtop-20260829T215641Z/src
/opt/everleaf/web.pre-gtop-20260829T215641Z/test
/opt/everleaf/web/data
/opt/everleaf/web/node_modules
/opt/everleaf/web/ops
/opt/everleaf/web/public
/opt/everleaf/web/scripts
/opt/everleaf/web/sql
/opt/everleaf/web/src
/opt/everleaf/web/test

=== likely server repositories ===
repo=/opt/everleaf/server
content-dev
ddc579c1124eabf5b2a72a303281fd7e1b6c3fa4
 M database/sql/1-db_database.sql
 M database/sql/migration/everleaf_rooted_forge.sql
 M mvnw
 M src/main/java/client/Character.java
 M src/main/java/client/Client.java
 M src/main/java/client/command/CommandsExecutor.java
 M src/main/java/client/command/commands/gm0/ReadPointsCommand.java
 M src/main/java/constants/game/ExpTable.java
 M src/main/java/net/server/Server.java
 M src/main/java/net/server/channel/handlers/PlayerLoggedinHandler.java
?? config.yaml.pre-8ch
?? src/main/java/client/command/commands/gm0/ReadPointsCommand.java.pre-nx
?? src/main/java/client/command/commands/gm0/VoteCommand.java
?? src/main/java/service/NxRewardService.java

=== production git diff summary ===
 database/sql/1-db_database.sql                     | 18187 ++++++++++++++++++-
 database/sql/migration/everleaf_rooted_forge.sql   |    17 +-
 mvnw                                               |     0
 src/main/java/client/Character.java                |    14 +-
 src/main/java/client/Client.java                   |     2 +
 src/main/java/client/command/CommandsExecutor.java |    12 +-
 .../command/commands/gm0/ReadPointsCommand.java    |    75 +-
 src/main/java/constants/game/ExpTable.java         |     9 +-
 src/main/java/net/server/Server.java               |     6 +-
 .../channel/handlers/PlayerLoggedinHandler.java    |     2 +
 10 files changed, 18295 insertions(+), 29 deletions(-)
M	database/sql/1-db_database.sql
M	database/sql/migration/everleaf_rooted_forge.sql
M	mvnw
M	src/main/java/client/Character.java
M	src/main/java/client/Client.java
M	src/main/java/client/command/CommandsExecutor.java
M	src/main/java/client/command/commands/gm0/ReadPointsCommand.java
M	src/main/java/constants/game/ExpTable.java
M	src/main/java/net/server/Server.java
M	src/main/java/net/server/channel/handlers/PlayerLoggedinHandler.java

=== docker ===
Docker version 29.1.3, build 29.1.3-0ubuntu3~24.04.2
Docker Compose version 2.40.3+ds1-0ubuntu1~24.04.1
NAMES                   IMAGE                 STATUS                  PORTS
everleaf-qa-qa-game-1   everleaf-qa-qa-game   Up 32 hours             127.0.0.1:17575->7575/tcp, 127.0.0.1:17576->7576/tcp, 127.0.0.1:17577->7577/tcp, 127.0.0.1:17578->7578/tcp, 127.0.0.1:17579->7579/tcp, 127.0.0.1:17580->7580/tcp, 127.0.0.1:17581->7581/tcp, 127.0.0.1:17582->7582/tcp, 127.0.0.1:18484->8484/tcp
everleaf-qa-qa-db-1     mysql:8.4.0           Up 33 hours (healthy)   33060/tcp, 127.0.0.1:13307->3306/tcp

=== everleaf systemd units ===
  UNIT                          LOAD   ACTIVE   SUB     DESCRIPTION
  everleaf-backup.service       loaded inactive dead    Back up EverLeaf production databases and configuration
  everleaf-discord.service      loaded active   running EverLeaf Discord Status Bot
  everleaf-disk-monitor.service loaded inactive dead    Check Everleaf staging disk usage
  everleaf-web.service          loaded active   running EverLeaf Website and CMS
  everleaf.service              loaded active   running Everleaf Enhanced Classic v83 staging server

Legend: LOAD   → Reflects whether the unit definition was properly loaded.
        ACTIVE → The high-level unit activation state, i.e. generalization of SUB.
        SUB    → The low-level unit activation state, values depend on unit type.

5 loaded units listed.
To show all installed unit files use 'systemctl list-unit-files'.

=== everleaf service execution ===
MainPID=480195
ExecStart={ path=/usr/bin/java ; argv[]=/usr/bin/java -Xms1g -Xmx6g -jar /opt/everleaf/current/target/everleaf-server-1.0-SNAPSHOT.jar ; ignore_errors=no ; start_time=[Sun 2026-08-30 18:50:10 UTC] ; stop_time=[n/a] ; pid=480195 ; code=(null) ; status=0/0 }
WorkingDirectory=/opt/everleaf/current
FragmentPath=/etc/systemd/system/everleaf.service
process cwd: /opt/everleaf/releases/6fecd6fcb1810df6d92e5d787e838030ece6acba
process exe: /usr/lib/jvm/java-21-openjdk-arm64/bin/java

=== release pointers ===
lrwxrwxrwx 1 ubuntu ubuntu 63 Aug 30 18:50 /opt/everleaf/current -> /opt/everleaf/releases/6fecd6fcb1810df6d92e5d787e838030ece6acba
/opt/everleaf/current -> /opt/everleaf/releases/6fecd6fcb1810df6d92e5d787e838030ece6acba
drwxrwxr-x 15 ubuntu ubuntu 4096 Aug 30 03:04 /opt/everleaf/server
/opt/everleaf/server -> /opt/everleaf/server

=== mysql runtime ===
mysql.service: active
mariadb.service: inactive
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess                            
LISTEN 0      4096       127.0.0.1:13307      0.0.0.0:*                                      
LISTEN 0      151        127.0.0.1:3306       0.0.0.0:*                                      

=== game ports ===
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess                            
LISTEN 0      4096               *:7575             *:*    users:(("java",pid=480195,fd=41)) 
LISTEN 0      4096               *:7580             *:*    users:(("java",pid=480195,fd=126))
LISTEN 0      4096               *:7581             *:*    users:(("java",pid=480195,fd=143))
LISTEN 0      4096               *:7582             *:*    users:(("java",pid=480195,fd=160))
LISTEN 0      4096               *:7576             *:*    users:(("java",pid=480195,fd=58)) 
LISTEN 0      4096               *:7577             *:*    users:(("java",pid=480195,fd=75)) 
LISTEN 0      4096               *:7578             *:*    users:(("java",pid=480195,fd=92)) 
LISTEN 0      4096               *:7579             *:*    users:(("java",pid=480195,fd=109))
LISTEN 0      4096               *:8484             *:*    users:(("java",pid=480195,fd=177))

=== compose files ===
/opt/everleaf/nx-rewards-test/docker-compose.yml
/opt/everleaf/releases/6fecd6fcb1810df6d92e5d787e838030ece6acba/docker-compose.yml
/opt/everleaf/releases/d3208973c9967845f2485169a9f59aa2dd0ce1c2/docker-compose.yml
/opt/everleaf/releases/e5295ad29544e496b0141dce7ba2ab43507a311e/docker-compose.yml
/opt/everleaf/releases/d6d30d03376694a39f9704f00f72b588c11cab1c/docker-compose.yml
/opt/everleaf/releases/9908d278ed7385b69fc1dd2abe1bee924b77c8ba/docker-compose.yml
/opt/everleaf/releases/631d51d22fd8ba0a2da4e45a0ae8ebab7ad4e2ef/docker-compose.yml
/opt/everleaf/releases/fa9178708974eaedba11cf4ec20326c2780521a9/docker-compose.yml
/opt/everleaf/releases/a5b5e41829abfc61d677758500b0dc6f252d3041/docker-compose.yml
/opt/everleaf/server/docker-compose.yml
/opt/everleaf/qa-agent-hub/docker-compose.yml

Production inspection complete. No state was changed.
```
