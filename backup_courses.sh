# Path where to store backup file.
# ie: /var/data/tmpback
destination=/var/www/html

# Declare the courses array
# This array contains all the courses to be exported.
declare -a courses=(199 185 188 195 183 182 189 163 178 160 4 155 153)

GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "\n"

for courseid in "${courses[@]}"
do
    echo -e "\n"
    echo -e "${GREEN}Exporting: $courseid to $destination.${NC}"
    echo -e "\n"
    php admin/cli/backup.php --courseid=$courseid --destination=$destination
    echo -e "\n"
done