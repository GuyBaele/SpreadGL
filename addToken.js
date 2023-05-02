#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const filePath = path.resolve(__dirname, './src/components/app.js');
const [, , newToken] = process.argv;

if (!newToken) {
    console.error('No Mapbox Access Token provided. Please provide your token as an argument.');
    process.exit(1);
}

fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
        console.error(`Error reading file: ${err}`);
        process.exit(1);
    }

    const updatedData = data.replace(/const mapboxAccessToken = .+;/, `const mapboxAccessToken = "${newToken}";`);

    fs.writeFile(filePath, updatedData, 'utf8', (err) => {
        if (err) {
            console.error(`Error writing file: ${err}`);
            process.exit(1);
        }

        console.log(`Successfully updated the Mapbox Access Token as "${newToken}"!`);
    });
});
