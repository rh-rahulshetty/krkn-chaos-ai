set -e

export HOST=${HOST:-}

# If HOST is not set, use the hostname of the service rs (nginx-proxy)
if [ -z "$HOST" ]; then
    export NGINX_ROUTE="http://$(kubectl get service rs -o json | jq -r '.status.loadBalancer.ingress[0].hostname')"
else
    export NGINX_ROUTE="$HOST"
fi

echo "NGINX_ROUTE: $NGINX_ROUTE"

# function to evaluate non-200 status code
function evaluate_status_code() {
    local url=$1
    local expected_status_code=$2
    local response=$(curl -s -o /dev/null -w "%{http_code}" $NGINX_ROUTE$url)
    if [ $response -ne $expected_status_code ]; then
        echo "$url FAILED"
        # exit 1
    else
        echo "$url OK"
    fi
}

evaluate_status_code /cart/health 200
evaluate_status_code /cart/add/1/Watson/1 200

evaluate_status_code /catalogue/health 200
evaluate_status_code /catalogue/categories 200
evaluate_status_code /catalogue/products 200

evaluate_status_code /payment/health 200

evaluate_status_code /ratings/_health 200
evaluate_status_code /ratings/api/fetch/Watson 200

evaluate_status_code /shipping/health 200
evaluate_status_code /shipping/codes 200

evaluate_status_code /user/health 200
evaluate_status_code /user/uniqueid 200

evaluate_status_code /web/ 200
