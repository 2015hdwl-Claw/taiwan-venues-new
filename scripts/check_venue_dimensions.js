const fs = require('fs');

const venues = JSON.parse(fs.readFileSync('venues.json', 'utf8'));
const venueIds = [1075, 1076, 1072, 1077];

venueIds.forEach(venueId => {
    const venue = venues.find(v => v.id === venueId);
    if (!venue) return;

    console.log(`\n${venue.name} (ID: ${venueId})`);
    console.log('='.repeat(60));

    venue.rooms.forEach(room => {
        const hasDimensions = !!room.dimensions;
        const hasLength = !!room.length;
        const hasWidth = !!room.width;
        const hasHeight = !!(room.height || room.ceiling);

        const status = hasDimensions ? '✓' : (hasLength && hasWidth && hasHeight ? '?' : '✗');
        console.log(`  ${status} ${room.name} (${room.id})`);
        console.log(`     dimensions: ${room.dimensions || '無'}`);
        console.log(`     length: ${room.length || '無'}, width: ${room.width || '無'}, height: ${room.height || room.ceiling || '無'}`);
        console.log(`     area: ${room.area || '無'} ${room.areaUnit || ''}`);
    });
});
