GALAXY_INSTANCE=$1
API_KEY=$2

for lock_file in $(ls $DIR_WITH_LOCK_FILES | grep .lock); do
  name=$( echo $lock_file | sed 's/.yaml.lock//' )
  shed-tools install --install_resolver_dependencies \
    --toolsfile $lock_file \
    --galaxy $GALAXY_INSTANCE \
    --api_key $API_KEY 2>&1 | tee -a $name.log
done
