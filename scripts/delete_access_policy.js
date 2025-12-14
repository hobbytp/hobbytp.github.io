const https = require('https');

const accountId = '026b92ea77fb94b88f6849fa335e554e';
// Accept token from command line argument
const token = process.argv[2];

if (!token) {
  console.error("Usage: node scripts/delete_access_policy.js <YOUR_API_TOKEN>");
  process.exit(1);
}

function makeRequest(path, method) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.cloudflare.com',
      path: path,
      method: method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve({ statusCode: res.statusCode, data: JSON.parse(data) });
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.end();
  });
}

async function main() {
  try {
    console.log("Searching for Access Applications...");
    const listRes = await makeRequest(`/client/v4/accounts/${accountId}/access/apps`, 'GET');

    if (!listRes.data.success) {
      console.error("Failed to list apps:", JSON.stringify(listRes.data.errors, null, 2));
      return;
    }

    const apps = listRes.data.result;
    const targetApp = apps.find(app => app.name.includes('hobbytp-github-io') || app.domain.includes('hobbytp-github-io'));

    if (!targetApp) {
      console.log("No Access Application found for 'hobbytp-github-io'.");
      console.log("Found apps:", apps.map(a => a.name).join(', '));
      return;
    }

    console.log(`Found Application: ${targetApp.name} (ID: ${targetApp.id})`);
    console.log("Deleting...");

    const deleteRes = await makeRequest(`/client/v4/accounts/${accountId}/access/apps/${targetApp.id}`, 'DELETE');

    if (deleteRes.data.success) {
      console.log("Successfully deleted Access Policy!");
    } else {
      console.error("Failed to delete:", JSON.stringify(deleteRes.data.errors, null, 2));
    }

  } catch (error) {
    console.error("Error:", error);
  }
}

main();
