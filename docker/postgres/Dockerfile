FROM postgres

# add backup scripts
ADD backup.sh /usr/local/bin/backup
ADD restore.sh /usr/local/bin/restore
ADD list-backups.sh /usr/local/bin/list-backups
ADD create-db.sh /usr/local/bin/create-db

# make them executable
RUN chmod +x /usr/local/bin/restore
RUN chmod +x /usr/local/bin/list-backups
RUN chmod +x /usr/local/bin/backup
RUN chmod +x /usr/local/bin/create-db

RUN create-db