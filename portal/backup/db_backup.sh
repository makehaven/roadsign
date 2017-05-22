POSTGRES_USER="postgres"
backup_dir="/backup/"
backup_name=$backup_dir`date +%Y.%m.%d-%H:%M`
pg_dump -U $POSTGRES_USER -Fc > $backup_name