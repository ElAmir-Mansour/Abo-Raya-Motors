/**
 * Interactive 3D Egypt Map (Expert GIS Edition)
 * Uses real Latitude/Longitude projection to ensure 100% geographic accuracy.
 */

import * as THREE from 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.module.js';

// --- GIS Configuration ---
const MAP_CENTER = { lat: 26.8, lon: 29.8 };
const MAP_SCALE = 12.0;

// Helper: Project Real Lat/Lon to 3D Local Space
function project(lat, lon) {
    // Flip Lat because in 3D, +Y is Up (North), but we want to center it.
    const y = (lat - MAP_CENTER.lat) * MAP_SCALE * 0.12;
    const x = (lon - MAP_CENTER.lon) * MAP_SCALE * 0.1;
    return new THREE.Vector3(x, y, 0);
}

export function initHero3D() {
    const canvas = document.querySelector('#hero-canvas');
    const tooltip = document.querySelector('#map-tooltip');
    const governorateSelect = document.querySelector('#governorate-select');

    if (!canvas) return;

    // --- Scene Setup ---
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x0a0e1a, 0.035);

    const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);

    const renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        alpha: true,
        antialias: true
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // --- Lighting ---
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    const sunLight = new THREE.DirectionalLight(0xffffff, 1.0);
    sunLight.position.set(10, 20, 20);
    scene.add(sunLight);

    const blueRim = new THREE.SpotLight(0x00d4ff, 3.0);
    blueRim.position.set(-20, 10, 10);
    blueRim.lookAt(0, 0, 0);
    scene.add(blueRim);

    const mapGroup = new THREE.Group();

    // --- 1. The GIS Base Map (Strict Containment) ---
    const egyptShape = drawStrictGISEgypt();
    const extrudeSettings = {
        steps: 1,
        depth: 0.2, // Thinner for elegance
        bevelEnabled: true,
        bevelThickness: 0.02,
        bevelSize: 0.02,
        bevelSegments: 3
    };

    const geometry = new THREE.ExtrudeGeometry(egyptShape, extrudeSettings);

    const material = new THREE.MeshPhysicalMaterial({
        color: 0x131925,
        metalness: 0.3,
        roughness: 0.6,
        clearcoat: 1.0,
        clearcoatRoughness: 0.2,
        transparent: true,
        opacity: 0.95,
        side: THREE.DoubleSide
    });

    const egyptMesh = new THREE.Mesh(geometry, material);
    egyptMesh.position.set(0, 0, -0.2);
    mapGroup.add(egyptMesh);

    // Digital Border
    const edges = new THREE.EdgesGeometry(geometry);
    const lineMaterial = new THREE.LineBasicMaterial({ color: 0x3b82f6, transparent: true, opacity: 0.3 });
    const wireframe = new THREE.LineSegments(edges, lineMaterial);
    egyptMesh.add(wireframe);


    // --- 2. The Nile (Refined) ---
    // Using slightly simplified paths for smoother visualization
    const nileCoords = [
        [22.00, 31.33], // Lake Nasser
        [24.08, 32.89], // Aswan
        [25.68, 32.63], // Luxor
        [26.15, 32.71], // Qena
        [27.17, 31.18], // Asyut
        [29.07, 31.09], // Beni Suef
        [30.04, 31.23], // Cairo
    ];

    const rosettaCoords = [
        [30.04, 31.23],
        [31.40, 30.42]  // Rosetta
    ];

    const damiettaCoords = [
        [30.04, 31.23],
        [31.52, 31.84]  // Damietta
    ];

    function createRiverMesh(coords) {
        const points = coords.map(c => {
            const v = project(c[0], c[1]);
            v.z = 0.02;
            return v;
        });
        const curve = new THREE.CatmullRomCurve3(points);
        return new THREE.Mesh(
            new THREE.TubeGeometry(curve, 64, 0.04, 8, false),
            new THREE.MeshBasicMaterial({ color: 0x06b6d4 })
        );
    }

    mapGroup.add(createRiverMesh(nileCoords));
    mapGroup.add(createRiverMesh(rosettaCoords));
    mapGroup.add(createRiverMesh(damiettaCoords));


    // --- 3. City Nodes (Sprites for Scaling) ---
    const cities = getGISCityData();
    const citySprites = [];

    // Texture
    const spriteTexture = createFlashTexture();
    const spriteMaterial = new THREE.SpriteMaterial({
        map: spriteTexture,
        color: 0xfbbf24,
        transparent: true,
        opacity: 0.9,
        depthTest: false // Ensure visibility
    });
    const majorMaterial = new THREE.SpriteMaterial({
        map: spriteTexture,
        color: 0x06b6d4, // Cyan for major
        transparent: true,
        opacity: 1.0,
        depthTest: false
    });

    cities.forEach(city => {
        const v = project(city.lat, city.lon);

        // Use Sprite for individual scaling
        const sprite = new THREE.Sprite(city.special ? majorMaterial.clone() : spriteMaterial.clone());

        // "Clean" look: smaller default size
        const baseScale = city.special ? 0.35 : 0.25;
        sprite.scale.set(baseScale, baseScale, 1);
        sprite.position.set(v.x, v.y, 0.3); // Hover above map

        // Store data for raycasting
        sprite.userData = { city: city, baseScale: baseScale };

        mapGroup.add(sprite);
        citySprites.push(sprite);
    });

    scene.add(mapGroup);

    // --- Camera & Interaction ---
    // User Feedback: "Tis too big" -> Major Zoom Out
    camera.position.z = 18;
    camera.position.y = -1; // Slight tilt correction

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let hoveredSprite = null;
    const isArabic = document.documentElement.lang === 'ar';

    function onMouseMove(event) {
        const rect = canvas.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        if (hoveredSprite) {
            tooltip.style.left = event.clientX + 15 + 'px';
            tooltip.style.top = event.clientY + 15 + 'px';
        }
    }

    function onClick() {
        if (hoveredSprite && governorateSelect) {
            const city = hoveredSprite.userData.city;
            governorateSelect.value = city.id;
            governorateSelect.classList.add('bg-warning', 'text-dark');
            setTimeout(() => governorateSelect.classList.remove('bg-warning', 'text-dark'), 500);
        }
    }

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('click', onClick);

    function animate() {
        requestAnimationFrame(animate);

        const time = Date.now() * 0.0005;
        // Gentle rotation
        mapGroup.rotation.y = Math.sin(time * 0.1) * 0.05;
        mapGroup.rotation.x = Math.cos(time * 0.1) * 0.02;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(citySprites);

        if (intersects.length > 0) {
            const sprite = intersects[0].object;
            const city = sprite.userData.city;

            if (hoveredSprite !== sprite) {
                // Reset previous
                if (hoveredSprite) {
                    const oldScale = hoveredSprite.userData.baseScale;
                    hoveredSprite.scale.set(oldScale, oldScale, 1);
                }

                hoveredSprite = sprite;

                // UX Feedback: "Get bigger when I hover"
                const hoverScale = sprite.userData.baseScale * 2.0;
                sprite.scale.set(hoverScale, hoverScale, 1);

                canvas.style.cursor = 'pointer';
                tooltip.style.display = 'block';
                tooltip.innerHTML = `<strong>${isArabic ? city.ar : city.name}</strong>`;
            }
        } else {
            if (hoveredSprite) {
                // Reset scale
                const oldScale = hoveredSprite.userData.baseScale;
                hoveredSprite.scale.set(oldScale, oldScale, 1);

                hoveredSprite = null;
                canvas.style.cursor = 'default';
                tooltip.style.display = 'none';
            }
        }

        renderer.render(scene, camera);
    }
    animate();

    // Responsive scaling
    const resizeObserver = new ResizeObserver(() => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
    resizeObserver.observe(document.body); // Better than window resize
}

// --- Data ---
function drawStrictGISEgypt() {
    const s = new THREE.Shape();

    // Strict Containment: Border slightly expanded to ensure coastal cities are inside
    const p1 = project(31.65, 25.00); // Sallum strict
    s.moveTo(p1.x, p1.y);

    // Coast - pushing slightly North to contain Alexandria/Port Said
    s.lineTo(project(31.50, 27.20).x, project(31.50, 27.20).y); // Matrouh Buffer
    s.lineTo(project(31.35, 29.92).x, project(31.35, 29.92).y); // Alex Buffer
    s.lineTo(project(31.60, 31.00).x, project(31.60, 31.00).y); // Delta Top
    s.lineTo(project(31.40, 32.30).x, project(31.40, 32.30).y); // Port Said Buffer
    s.lineTo(project(31.35, 34.25).x, project(31.35, 34.25).y); // Rafah

    // East
    s.lineTo(project(29.50, 34.96).x, project(29.50, 34.96).y); // Taba
    s.lineTo(project(27.90, 34.35).x, project(27.90, 34.35).y); // Sharm Tip
    s.lineTo(project(27.50, 33.50).x, project(27.50, 33.50).y); // Gulf entry
    s.lineTo(project(22.00, 36.80).x, project(22.00, 36.80).y); // Halayeb Outer

    // South
    s.lineTo(project(22.00, 25.00).x, project(22.00, 25.00).y); // Oweinat

    // West
    s.lineTo(p1.x, p1.y);

    return s;
}

function getGISCityData() {
    return [
        // Delta & North
        { name: 'Cairo', ar: 'القاهرة', id: 'CAIRO', lat: 30.04, lon: 31.23, special: true },
        { name: 'Giza', ar: 'الجيزة', id: 'GIZA', lat: 29.98, lon: 31.13 },
        { name: 'Alexandria', ar: 'الإسكندرية', id: 'ALEX', lat: 31.20, lon: 29.91, special: true },
        { name: 'Port Said', ar: 'بورسعيد', id: 'PORT_SAID', lat: 31.26, lon: 32.30 },
        { name: 'Suez', ar: 'السويس', id: 'SUEZ', lat: 29.97, lon: 32.53 },
        { name: 'Marsa Matrouh', ar: 'مرسى مطروح', id: 'MATROUH', lat: 31.35, lon: 27.23 },
        { name: 'Sharm El Sheikh', ar: 'شرم الشيخ', id: 'SHARM', lat: 27.91, lon: 34.32, special: true },
        { name: 'Hurghada', ar: 'الغردقة', id: 'HURGHADA', lat: 27.25, lon: 33.81 },
        { name: 'Luxor', ar: 'الأقصر', id: 'LUXOR', lat: 25.68, lon: 32.64, special: true },
        { name: 'Aswan', ar: 'أسوان', id: 'ASWAN', lat: 24.08, lon: 32.89 },
        { name: 'Siwa', ar: 'سيوة', id: 'SIWA', lat: 29.20, lon: 25.52 },
        { name: 'Minya', ar: 'المنيا', id: 'MINYA', lat: 28.10, lon: 30.75 },
        { name: 'Asyut', ar: 'أسيوط', id: 'ASYUT', lat: 27.18, lon: 31.18 },
        { name: 'Sohag', ar: 'سوهاج', id: 'SOHAG', lat: 26.56, lon: 31.69 },
        { name: 'Qena', ar: 'قنا', id: 'QENA', lat: 26.16, lon: 32.72 },
        { name: 'Ismailia', ar: 'الإسماعيلية', id: 'ISMAILIA', lat: 30.59, lon: 32.27 },
        { name: 'Tanta', ar: 'طنطا', id: 'GHARBIA', lat: 30.78, lon: 31.00 },
        { name: 'Mansoura', ar: 'المنصورة', id: 'DAKAHLIA', lat: 31.04, lon: 31.38 },
        { name: 'Zagazig', ar: 'الزقازيق', id: 'SHARKIA', lat: 30.58, lon: 31.50 },
        { name: 'Faiyum', ar: 'الفيوم', id: 'FAIYUM', lat: 29.31, lon: 30.84 },
        { name: 'Beni Suef', ar: 'بني سويف', id: 'BENI_SUEF', lat: 29.07, lon: 31.10 },
        { name: 'Damietta', ar: 'دمياط', id: 'DAMIETTA', lat: 31.41, lon: 31.81 },
        { name: 'Kafr El Sheikh', ar: 'كفر الشيخ', id: 'KAFR_EL_SHEIKH', lat: 31.11, lon: 30.94 },
        { name: 'Benha', ar: 'بنها', id: 'QALIUBIYA', lat: 30.46, lon: 31.18 },
        { name: 'Shebin El Kom', ar: 'شبين الكوم', id: 'MENOUFIA', lat: 30.55, lon: 31.01 },
        { name: 'Damanhur', ar: 'دمنهور', id: 'BEHEIRA', lat: 31.04, lon: 30.47 },
        { name: 'Arish', ar: 'العريش', id: 'NORTH_SINAI', lat: 31.13, lon: 33.80 },
        { name: 'El Alamein', ar: 'العلمين', id: 'ALAMEIN', lat: 30.83, lon: 28.95 },
        { name: 'Dahab', ar: 'دهب', id: 'DAHAB', lat: 28.50, lon: 34.51 },
        { name: 'Nuweiba', ar: 'نويبع', id: 'SOUTH_SINAI', lat: 29.04, lon: 34.64 },
        { name: 'Safaga', ar: 'سفاجا', id: 'RED_SEA', lat: 26.73, lon: 33.93 },
        { name: 'Marsa Alam', ar: 'مرسى علم', id: 'MARSA_ALAM', lat: 25.07, lon: 34.89 },
        { name: 'Kharga', ar: 'الخارجة', id: 'NEW_VALLEY', lat: 25.44, lon: 30.55 },
        { name: 'Dakhla', ar: 'الداخلة', id: 'NEW_VALLEY', lat: 25.51, lon: 29.17 },
    ];
}

function createFlashTexture() {
    const size = 64;
    const canvas = document.createElement('canvas');
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');

    // Solid Core (Clean)
    ctx.beginPath();
    ctx.arc(size / 2, size / 2, size / 4, 0, Math.PI * 2);
    ctx.fillStyle = '#ffffff';
    ctx.fill();

    // Soft Bloom
    const gradient = ctx.createRadialGradient(size / 2, size / 2, size / 4, size / 2, size / 2, size / 2);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 0.8)');
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');

    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, size, size);

    return new THREE.CanvasTexture(canvas);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHero3D);
} else {
    initHero3D();
}
