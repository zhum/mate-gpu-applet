сurl -s 'https://finnhub.io/api/v1/quote?token=$TOKEN&symbol=NVDA'




#| jq -r '. | "'$i': " + ((.c*10 | floor) / 10 | tostring) + " [" + ((.l*10 | floor)/10 | tostring) + ".."+ ((.h*10 | floor)/10 | tostring) + "]"'