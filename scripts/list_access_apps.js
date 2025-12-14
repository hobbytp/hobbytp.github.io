
const https = require('https');

const accountId = '026b92ea77fb94b88f6849fa335e554e';
const token = process.env.CLOUDFLARE_API_TOKEN;

if (!token) {
  console.error("CLOUDFLARE_API_TOKEN is not set in the environment.");
  // Try to see if we can find it in wrangler config or similar, but for now just fail.
  process.exit(1);
}

const options = {
  hostname: 'api.cloudflare.com',
  path: `/client/v4/accounts/${accountId}/access/apps`,
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
};

const req = https.request(options, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    try {
        const json = JSON.parse(data);
        if (res.statusCode >= 200 && res.statusCode < 300 && json.success) {
            json.result.forEach(app => {
                console.log(`FOUND_APP: ${app.name} | ${app.id} | ${app.domain}`);
            });
            if (json.result.length === 0) {
                console.log("No Access Applications found.");
            }
        } else {
            console.error('API Error:', JSON.stringify(json, null, 2));
        }
    } catch (e) {
        console.error("Failed to parse response:", data);
    }
  });
});

req.on('error', (e) => {
  console.error('Request Error:', e);
});

req.end();
