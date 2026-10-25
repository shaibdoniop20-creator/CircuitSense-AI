/**
 * CircuitSense AI - Real-Time 3D PCB Assembly & Exploded View Experience
 * Powered by Three.js & GSAP ScrollTrigger
 * 
 * Features:
 * - High-fidelity procedural green PCB with copper routing traces, solder pads, gold contacts & silkscreen
 * - Independently animated component groups (MCU, ICs, Capacitors, Transistors, Connectors)
 * - 4-Stage Scroll Sequence: Exploded View -> Approach -> Assembly -> Completion
 * - Dynamic SVG leader lines tracking 3D world coordinates projected to 2D screen space
 * - Translucent Liquid Glass information panels with sample data disclaimers
 * - Physically based materials, soft studio lighting, realistic contact shadows
 * - Full bidirectional scroll scrubbing and graceful WebGL / reduced-motion fallbacks
 */

(function () {
  'use strict';

  // Check if WebGL is supported
  function isWebGLAvailable() {
    try {
      const canvas = document.createElement('canvas');
      return !!(window.WebGLRenderingContext && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
    } catch (e) {
      return false;
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('pcbCanvasContainer');
    const stage = document.getElementById('pcbStickyStage');
    const fallback = document.getElementById('pcbFallbackView');
    const section = document.getElementById('pcbExperienceSection');

    if (!container || !stage || !section) return;

    if (!isWebGLAvailable() || typeof THREE === 'undefined') {
      if (fallback) fallback.style.display = 'flex';
      if (container) container.style.display = 'none';
      return;
    }

    initPCBScene(container, stage, section);
  });

  function initPCBScene(container, stage, section) {
    // -------------------------------------------------------------------------
    // 1. SCENE, CAMERA & RENDERER SETUP (Stitch Warm Ivory Environment)
    // -------------------------------------------------------------------------
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0xfcf9ef, 0.015);

    const width = container.clientWidth || window.innerWidth;
    const height = container.clientHeight || 750;

    const camera = new THREE.PerspectiveCamera(38, width / height, 0.1, 100);
    // Initial camera position for Exploded View
    camera.position.set(0, 11, 17);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance'
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(width, height);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    if (THREE.ACESFilmicToneMapping) {
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.08;
    }
    if (THREE.sRGBEncoding) {
      renderer.outputEncoding = THREE.sRGBEncoding;
    }
    container.appendChild(renderer.domElement);

    // -------------------------------------------------------------------------
    // 2. LIGHTING & ATMOSPHERE (Light Studio Setup)
    // -------------------------------------------------------------------------
    // Soft ambient illumination
    const ambientLight = new THREE.AmbientLight(0xffffff, 1.3);
    scene.add(ambientLight);

    // Hemisphere light: warm ivory studio sky, champagne ceramic ground reflection
    const hemiLight = new THREE.HemisphereLight(0xfffef9, 0xf1eee4, 0.95);
    hemiLight.position.set(0, 25, 0);
    scene.add(hemiLight);

    // Main Directional Key Light (casting soft shadows)
    const keyLight = new THREE.DirectionalLight(0xffffff, 1.6);
    keyLight.position.set(8, 16, 10);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.width = 2048;
    keyLight.shadow.mapSize.height = 2048;
    keyLight.shadow.camera.near = 0.5;
    keyLight.shadow.camera.far = 40;
    const d = 12;
    keyLight.shadow.camera.left = -d;
    keyLight.shadow.camera.right = d;
    keyLight.shadow.camera.top = d;
    keyLight.shadow.camera.bottom = -d;
    keyLight.shadow.bias = -0.0004;
    keyLight.shadow.radius = 3.5;
    scene.add(keyLight);

    // Soft cool fill light from opposite side
    const fillLight = new THREE.DirectionalLight(0xe0f2fe, 0.75);
    fillLight.position.set(-10, 10, -6);
    scene.add(fillLight);

    // Warm specular rim light to make traces and pins pop
    const rimLight = new THREE.DirectionalLight(0xfef3c7, 0.65);
    rimLight.position.set(0, 8, -12);
    scene.add(rimLight);

    // -------------------------------------------------------------------------
    // 3. MASTER PCB GROUP
    // -------------------------------------------------------------------------
    const pcbMasterGroup = new THREE.Group();
    // Exploded View initial tilt
    pcbMasterGroup.rotation.set(0.42, -0.45, 0.15);
    scene.add(pcbMasterGroup);

    // -------------------------------------------------------------------------
    // 4. PROCEDURAL PCB TEXTURE GENERATION (Traces, Silkscreen, Solder Pads)
    // -------------------------------------------------------------------------
    function generatePCBTexture() {
      const texCanvas = document.createElement('canvas');
      texCanvas.width = 2048;
      texCanvas.height = 1400;
      const ctx = texCanvas.getContext('2d');

      // Deep, rich green solder mask lacquer base
      const bgGrad = ctx.createLinearGradient(0, 0, 2048, 1400);
      bgGrad.addColorStop(0, '#155e2d');
      bgGrad.addColorStop(0.5, '#166534');
      bgGrad.addColorStop(1, '#14532d');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, 2048, 1400);

      // Subtle board copper pour ground plane hatch
      ctx.strokeStyle = 'rgba(21, 94, 45, 0.45)';
      ctx.lineWidth = 1;
      for (let x = 0; x < 2048; x += 16) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, 1400);
        ctx.stroke();
      }

      // Copper routing traces (Rich metallic gold/copper)
      ctx.strokeStyle = '#d4af37';
      ctx.lineWidth = 4;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      // Draw realistic routing bus traces
      const traces = [
        // Central MCU Bus lines
        [[1024, 700], [1024, 820], [860, 984], [520, 984], [440, 1064], [440, 1260]],
        [[1044, 700], [1044, 840], [880, 1004], [540, 1004], [460, 1084], [460, 1260]],
        [[1064, 700], [1064, 860], [900, 1024], [560, 1024], [480, 1104], [480, 1260]],
        [[984, 700], [984, 840], [1144, 1000], [1480, 1000], [1560, 1080], [1560, 1260]],
        [[964, 700], [964, 860], [1124, 1020], [1460, 1020], [1540, 1100], [1540, 1260]],
        
        // Horizontal logic buses to IC1 (left)
        [[780, 680], [620, 680], [540, 600], [540, 480], [420, 480]],
        [[780, 700], [640, 700], [560, 620], [560, 500], [420, 500]],
        [[780, 720], [660, 720], [580, 640], [580, 520], [420, 520]],
        
        // Buses to IC2 (right)
        [[1268, 680], [1428, 680], [1508, 600], [1508, 480], [1628, 480]],
        [[1268, 700], [1408, 700], [1488, 620], [1488, 500], [1628, 500]],
        [[1268, 720], [1388, 720], [1468, 640], [1468, 520], [1628, 520]],

        // Top power traces to voltage regulators & capacitors
        [[1024, 460], [1024, 300], [1180, 144], [1450, 144]],
        [[980, 460], [980, 280], [820, 120], [580, 120]]
      ];

      traces.forEach(path => {
        ctx.beginPath();
        ctx.moveTo(path[0][0], path[0][1]);
        for (let i = 1; i < path.length; i++) {
          ctx.lineTo(path[i][0], path[i][1]);
        }
        ctx.stroke();
      });

      // Solder vias & circular connection pads
      function drawVia(x, y, r = 7) {
        ctx.fillStyle = '#b8860b';
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#10391d';
        ctx.beginPath();
        ctx.arc(x, y, r * 0.45, 0, Math.PI * 2);
        ctx.fill();
      }

      // Draw pattern of gold vias
      for (let i = 0; i < 40; i++) {
        const vx = 300 + (i * 37) % 1450;
        const vy = 250 + (i * 53) % 900;
        drawVia(vx, vy, 6);
      }

      // Corner Mounting Holes with Gold Ground Rings
      const corners = [[100, 100], [1948, 100], [100, 1300], [1948, 1300]];
      corners.forEach(([cx, cy]) => {
        ctx.fillStyle = '#d4af37';
        ctx.beginPath();
        ctx.arc(cx, cy, 38, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#0f172a'; // Hole
        ctx.beginPath();
        ctx.arc(cx, cy, 24, 0, Math.PI * 2);
        ctx.fill();
      });

      // Gold Edge Connector Fingers (Bottom Edge)
      const fingerWidth = 22;
      const fingerHeight = 110;
      const fingerGap = 12;
      const startX = 400;
      const endX = 1648;
      ctx.fillStyle = '#d4af37';
      for (let fx = startX; fx < endX; fx += fingerWidth + fingerGap) {
        ctx.fillRect(fx, 1400 - fingerHeight, fingerWidth, fingerHeight);
        // Solder pad rounded tip
        ctx.beginPath();
        ctx.arc(fx + fingerWidth / 2, 1400 - fingerHeight, fingerWidth / 2, Math.PI, 0);
        ctx.fill();
      }

      // Silkscreen Markings (Crisp white vector legends & designators)
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 26px "Inter", sans-serif';
      ctx.fillText('CIRCUITSENSE AI', 200, 200);

      ctx.font = '600 16px "JetBrains Mono", monospace';
      ctx.fillStyle = 'rgba(255, 255, 255, 0.75)';
      ctx.fillText('NEURAL SPECTRAL DISMANTLING SYSTEM v4.2', 200, 230);
      ctx.fillText('REV: 03-LUMINOUS', 200, 255);

      // Component reference designators
      ctx.font = 'bold 18px "JetBrains Mono", monospace';
      ctx.fillStyle = '#ffffff';
      ctx.fillText('U1 [MCU]', 1024 - 40, 480);
      ctx.fillText('U2 [BUS_IC]', 420 - 45, 410);
      ctx.fillText('U3 [SPI_FLASH]', 1628 - 55, 410);
      ctx.fillText('C1', 1380, 1020);
      ctx.fillText('C2', 1580, 1020);
      ctx.fillText('Q1', 820, 1140);
      ctx.fillText('Q2', 1024, 1140);
      ctx.fillText('Q3', 1220, 1140);
      ctx.fillText('J1 [EXPANSION]', 140, 700);
      ctx.fillText('J2 [I/O PORT]', 1880, 700);

      // Fiducial cross alignment marks
      function drawFiducial(x, y) {
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x - 14, y); ctx.lineTo(x + 14, y);
        ctx.moveTo(x, y - 14); ctx.lineTo(x, y + 14);
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.stroke();
      }
      drawFiducial(150, 150);
      drawFiducial(1898, 150);
      drawFiducial(150, 1250);
      drawFiducial(1898, 1250);

      const texture = new THREE.CanvasTexture(texCanvas);
      texture.anisotropy = 8;
      return texture;
    }

    const pcbTexture = generatePCBTexture();

    // -------------------------------------------------------------------------
    // 5. CREATE PCB BASE BOARD MESH
    // -------------------------------------------------------------------------
    const pcbWidth = 18.0;
    const pcbThickness = 0.32;
    const pcbLength = 12.2;

    const boardMaterial = new THREE.MeshPhysicalMaterial({
      color: 0x166534,
      map: pcbTexture,
      roughness: 0.35,
      metalness: 0.12,
      clearcoat: 0.4,
      clearcoatRoughness: 0.18
    });

    const boardGeom = new THREE.BoxGeometry(pcbWidth, pcbThickness, pcbLength, 2, 1, 2);
    const pcbBoardMesh = new THREE.Mesh(boardGeom, boardMaterial);
    pcbBoardMesh.receiveShadow = true;
    pcbBoardMesh.castShadow = true;
    pcbMasterGroup.add(pcbBoardMesh);

    // Realistic Contact Shadow Plane under PCB
    function createContactShadow() {
      const shadowCanvas = document.createElement('canvas');
      shadowCanvas.width = 512;
      shadowCanvas.height = 512;
      const sCtx = shadowCanvas.getContext('2d');
      const grad = sCtx.createRadialGradient(256, 256, 40, 256, 256, 240);
      grad.addColorStop(0, 'rgba(132, 115, 91, 0.38)');
      grad.addColorStop(0.5, 'rgba(132, 115, 91, 0.16)');
      grad.addColorStop(1, 'rgba(132, 115, 91, 0)');
      sCtx.fillStyle = grad;
      sCtx.fillRect(0, 0, 512, 512);

      const sTex = new THREE.CanvasTexture(shadowCanvas);
      const sGeo = new THREE.PlaneGeometry(24, 18);
      const sMat = new THREE.MeshBasicMaterial({
        map: sTex,
        transparent: true,
        opacity: 0.75,
        depthWrite: false
      });
      const sMesh = new THREE.Mesh(sGeo, sMat);
      sMesh.rotation.x = -Math.PI / 2;
      sMesh.position.y = -0.9;
      return sMesh;
    }
    const contactShadow = createContactShadow();
    pcbMasterGroup.add(contactShadow);

    // -------------------------------------------------------------------------
    // 6. COMPONENT MATERIALS
    // -------------------------------------------------------------------------
    // Matte black IC chip epoxy resin
    const icBodyMaterial = new THREE.MeshStandardMaterial({
      color: 0x1c1e24,
      roughness: 0.55,
      metalness: 0.15
    });

    // Metallic silver pins & leads
    const pinMaterial = new THREE.MeshStandardMaterial({
      color: 0xe2e8f0,
      roughness: 0.22,
      metalness: 0.92
    });

    // Metallic gold connector contacts
    const goldMaterial = new THREE.MeshStandardMaterial({
      color: 0xd4af37,
      roughness: 0.25,
      metalness: 0.95
    });

    // Brushed aluminum capacitor top
    const aluMaterial = new THREE.MeshStandardMaterial({
      color: 0xe2e8f0,
      roughness: 0.28,
      metalness: 0.88
    });

    // Dark capacitor sleeve body
    const capBodyMaterial = new THREE.MeshStandardMaterial({
      color: 0x1e293b,
      roughness: 0.45,
      metalness: 0.2
    });

    // Ceramic SMD capacitor material
    const ceramicMaterial = new THREE.MeshStandardMaterial({
      color: 0xc8a27a,
      roughness: 0.5,
      metalness: 0.1
    });

    // Transistor cooling tab metal
    const heatsinkMaterial = new THREE.MeshStandardMaterial({
      color: 0xcbd5e1,
      roughness: 0.2,
      metalness: 0.9
    });

    // -------------------------------------------------------------------------
    // 7. COMPONENT FACTORIES & GROUPS (Independently Animated)
    // -------------------------------------------------------------------------

    // A. MICROCONTROLLER (U1 - LQFP-64 ARM Cortex-M4)
    const mcuGroup = new THREE.Group();
    {
      const bodyGeo = new THREE.BoxGeometry(3.8, 0.38, 3.8);
      const bodyMesh = new THREE.Mesh(bodyGeo, icBodyMaterial);
      bodyMesh.castShadow = true;
      bodyMesh.receiveShadow = true;
      mcuGroup.add(bodyMesh);

      // Pin-1 dot indicator
      const dotGeo = new THREE.CylinderGeometry(0.12, 0.12, 0.05, 12);
      const dotMesh = new THREE.Mesh(dotGeo, pinMaterial);
      dotMesh.position.set(-1.45, 0.2, -1.45);
      mcuGroup.add(dotMesh);

      // Laser etched text simulation plate
      const plateGeo = new THREE.PlaneGeometry(2.4, 2.4);
      const pCanvas = document.createElement('canvas');
      pCanvas.width = 256; pCanvas.height = 256;
      const pCtx = pCanvas.getContext('2d');
      pCtx.fillStyle = '#1c1e24';
      pCtx.fillRect(0, 0, 256, 256);
      pCtx.fillStyle = 'rgba(255, 255, 255, 0.4)';
      pCtx.font = 'bold 24px monospace';
      pCtx.fillText('ARM CORTEX', 45, 90);
      pCtx.fillText('STM32F405', 52, 130);
      pCtx.font = '16px monospace';
      pCtx.fillText('CS-AI SEC', 70, 165);
      const pTex = new THREE.CanvasTexture(pCanvas);
      const plateMat = new THREE.MeshBasicMaterial({ map: pTex });
      const plateMesh = new THREE.Mesh(plateGeo, plateMat);
      plateMesh.rotation.x = -Math.PI / 2;
      plateMesh.position.y = 0.2;
      mcuGroup.add(plateMesh);

      // 64 metallic leads (16 per side)
      const pinWidth = 0.08;
      const pinLength = 0.45;
      const pinThick = 0.04;
      const pinGeo = new THREE.BoxGeometry(pinWidth, pinThick, pinLength);

      for (let i = 0; i < 16; i++) {
        const offset = -1.5 + (i * 0.2);
        // North & South
        const pN = new THREE.Mesh(pinGeo, pinMaterial);
        pN.position.set(offset, -0.08, -2.1);
        mcuGroup.add(pN);

        const pS = new THREE.Mesh(pinGeo, pinMaterial);
        pS.position.set(offset, -0.08, 2.1);
        mcuGroup.add(pS);

        // East & West (rotated)
        const pE = new THREE.Mesh(pinGeo, pinMaterial);
        pE.rotation.y = Math.PI / 2;
        pE.position.set(2.1, -0.08, offset);
        mcuGroup.add(pE);

        const pW = new THREE.Mesh(pinGeo, pinMaterial);
        pW.rotation.y = Math.PI / 2;
        pW.position.set(-2.1, -0.08, offset);
        mcuGroup.add(pW);
      }
    }

    // B. INTEGRATED CIRCUITS (IC1: SOIC-20, IC2: SOIC-8, IC3: TSSOP-16)
    function createSOIC(pinsPerSide, width, length, label) {
      const g = new THREE.Group();
      const bodyGeo = new THREE.BoxGeometry(width, 0.32, length);
      const bMesh = new THREE.Mesh(bodyGeo, icBodyMaterial);
      bMesh.castShadow = true;
      bMesh.receiveShadow = true;
      g.add(bMesh);

      // Pin 1 dot
      const dotGeo = new THREE.CylinderGeometry(0.1, 0.1, 0.04, 10);
      const dMesh = new THREE.Mesh(dotGeo, pinMaterial);
      dMesh.position.set(-width / 2 + 0.3, 0.17, -length / 2 + 0.3);
      g.add(dMesh);

      // Pins on long sides
      const pinGeo = new THREE.BoxGeometry(0.35, 0.04, 0.1);
      const step = (length - 0.6) / (pinsPerSide - 1);
      for (let i = 0; i < pinsPerSide; i++) {
        const z = -length / 2 + 0.3 + (i * step);
        const pLeft = new THREE.Mesh(pinGeo, pinMaterial);
        pLeft.position.set(-width / 2 - 0.16, -0.06, z);
        g.add(pLeft);

        const pRight = new THREE.Mesh(pinGeo, pinMaterial);
        pRight.position.set(width / 2 + 0.16, -0.06, z);
        g.add(pRight);
      }
      return g;
    }

    const ic1Group = createSOIC(10, 2.2, 3.6, 'BUS_XCVR');
    const ic2Group = createSOIC(4, 1.8, 1.8, 'SPI_FLASH');
    const ic3Group = createSOIC(8, 2.0, 2.8, 'OP_AMP');

    // C. CAPACITORS (Electrolytic Aluminum Cans + Ceramic SMD)
    const capGroup = new THREE.Group();

    function createElectrolyticCap(radius, height) {
      const c = new THREE.Group();
      const bodyGeo = new THREE.CylinderGeometry(radius, radius, height, 24);
      const bodyMesh = new THREE.Mesh(bodyGeo, capBodyMaterial);
      bodyMesh.castShadow = true;
      bodyMesh.position.y = height / 2;
      c.add(bodyMesh);

      // Aluminum top with scored vent
      const topGeo = new THREE.CylinderGeometry(radius * 0.96, radius * 0.96, 0.04, 24);
      const topMesh = new THREE.Mesh(topGeo, aluMaterial);
      topMesh.position.y = height + 0.02;
      c.add(topMesh);

      // Base plastic spacer
      const baseGeo = new THREE.BoxGeometry(radius * 2.1, 0.1, radius * 2.1);
      const baseMesh = new THREE.Mesh(baseGeo, icBodyMaterial);
      baseMesh.position.y = 0.05;
      c.add(baseMesh);

      return c;
    }

    const cap1 = createElectrolyticCap(0.75, 1.9);
    cap1.position.set(4.6, 0, 2.4);
    capGroup.add(cap1);

    const cap2 = createElectrolyticCap(0.6, 1.5);
    cap2.position.set(6.4, 0, 2.4);
    capGroup.add(cap2);

    // Ceramic SMD Chip Capacitors
    function createSMDCap() {
      const c = new THREE.Group();
      const body = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.2, 0.5), ceramicMaterial);
      body.castShadow = true;
      body.position.y = 0.1;
      c.add(body);
      const endGeo = new THREE.BoxGeometry(0.31, 0.21, 0.1);
      const end1 = new THREE.Mesh(endGeo, pinMaterial);
      end1.position.set(0, 0.1, -0.21);
      const end2 = new THREE.Mesh(endGeo, pinMaterial);
      end2.position.set(0, 0.1, 0.21);
      c.add(end1, end2);
      return c;
    }
    const smd1 = createSMDCap(); smd1.position.set(-1.8, 0, -3.2); capGroup.add(smd1);
    const smd2 = createSMDCap(); smd2.position.set(1.8, 0, -3.2); capGroup.add(smd2);
    const smd3 = createSMDCap(); smd3.position.set(3.4, 0, -1.8); capGroup.add(smd3);

    // D. POWER TRANSISTORS (Q1, Q2, Q3 - SOT-223 / TO-220)
    const transistorGroup = new THREE.Group();

    function createTransistor() {
      const t = new THREE.Group();
      const bodyGeo = new THREE.BoxGeometry(1.2, 0.35, 0.8);
      const bodyMesh = new THREE.Mesh(bodyGeo, icBodyMaterial);
      bodyMesh.castShadow = true;
      t.add(bodyMesh);

      // Silver cooling heatsink tab
      const tabGeo = new THREE.BoxGeometry(1.0, 0.06, 0.5);
      const tabMesh = new THREE.Mesh(tabGeo, heatsinkMaterial);
      tabMesh.position.set(0, -0.05, -0.55);
      t.add(tabMesh);

      // 3 leads
      const leadGeo = new THREE.BoxGeometry(0.12, 0.04, 0.45);
      for (let i = -1; i <= 1; i++) {
        const lead = new THREE.Mesh(leadGeo, pinMaterial);
        lead.position.set(i * 0.35, -0.1, 0.55);
        t.add(lead);
      }
      return t;
    }

    const q1 = createTransistor(); q1.position.set(-2.0, 0.18, 3.2); transistorGroup.add(q1);
    const q2 = createTransistor(); q2.position.set(0.0, 0.18, 3.2); transistorGroup.add(q2);
    const q3 = createTransistor(); q3.position.set(2.0, 0.18, 3.2); transistorGroup.add(q3);

    // E. CONNECTORS (J1: Dual-row Gold Header, J2: Shielded USB-C / I/O)
    const connGroup = new THREE.Group();

    // J1: Dual-Row Pin Header
    const headerBlock = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.8, 4.6), icBodyMaterial);
    headerBlock.castShadow = true;
    headerBlock.position.set(-7.4, 0.4, 0);
    connGroup.add(headerBlock);

    // Gold pins inside header
    const pinStickGeo = new THREE.BoxGeometry(0.08, 1.4, 0.08);
    for (let r = 0; r < 2; r++) {
      for (let p = 0; p < 8; p++) {
        const pin = new THREE.Mesh(pinStickGeo, goldMaterial);
        pin.position.set(-7.6 + r * 0.4, 0.7, -1.8 + p * 0.52);
        connGroup.add(pin);
      }
    }

    // J2: Shielded Metal I/O Port
    const usbHousing = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.9, 2.2), aluMaterial);
    usbHousing.castShadow = true;
    usbHousing.position.set(7.5, 0.45, 0);
    connGroup.add(usbHousing);

    // Inner connector tongue
    const tongue = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.12, 1.6), icBodyMaterial);
    tongue.position.set(7.7, 0.45, 0);
    connGroup.add(tongue);

    // Add all component groups to master board group
    pcbMasterGroup.add(mcuGroup);
    pcbMasterGroup.add(ic1Group);
    pcbMasterGroup.add(ic2Group);
    pcbMasterGroup.add(ic3Group);
    pcbMasterGroup.add(capGroup);
    pcbMasterGroup.add(transistorGroup);
    pcbMasterGroup.add(connGroup);

    // -------------------------------------------------------------------------
    // 8. INITIALIZE EXPLODED VIEW COORDINATES & MOUNT DESTINATIONS
    // -------------------------------------------------------------------------
    // Final Mounted Positions (Y=0.18 on top of PCB substrate)
    const mountedPositions = {
      mcu: { x: 0, y: 0.18, z: 0, rx: 0, ry: 0, rz: 0 },
      ic1: { x: -4.8, y: 0.18, z: -2.4, rx: 0, ry: 0, rz: 0 },
      ic2: { x: 4.8, y: 0.18, z: -2.4, rx: 0, ry: 0, rz: 0 },
      ic3: { x: -4.8, y: 0.18, z: 2.2, rx: 0, ry: 0, rz: 0 },
      cap: { y: 0 },
      transistor: { y: 0.18 },
      conn: { y: 0 }
    };

    // Exploded View Floating Heights & Tilts (Hovering high above board)
    const explodedPositions = {
      mcu: { x: 0, y: 5.2, z: 0, rx: 0.08, ry: 0.05, rz: -0.06 },
      ic1: { x: -4.8, y: 4.5, z: -2.4, rx: -0.06, ry: 0.08, rz: 0.04 },
      ic2: { x: 4.8, y: 4.2, z: -2.4, rx: 0.05, ry: -0.06, rz: 0.08 },
      ic3: { x: -4.8, y: 3.9, z: 2.2, rx: 0.07, ry: 0.04, rz: -0.05 },
      cap: { y: 4.6 },
      transistor: { y: 4.1 },
      conn: { y: 4.4 }
    };

    // Apply Exploded View initially
    function applyExplodedState() {
      mcuGroup.position.set(explodedPositions.mcu.x, explodedPositions.mcu.y, explodedPositions.mcu.z);
      mcuGroup.rotation.set(explodedPositions.mcu.rx, explodedPositions.mcu.ry, explodedPositions.mcu.rz);

      ic1Group.position.set(explodedPositions.ic1.x, explodedPositions.ic1.y, explodedPositions.ic1.z);
      ic1Group.rotation.set(explodedPositions.ic1.rx, explodedPositions.ic1.ry, explodedPositions.ic1.rz);

      ic2Group.position.set(explodedPositions.ic2.x, explodedPositions.ic2.y, explodedPositions.ic2.z);
      ic2Group.rotation.set(explodedPositions.ic2.rx, explodedPositions.ic2.ry, explodedPositions.ic2.rz);

      ic3Group.position.set(explodedPositions.ic3.x, explodedPositions.ic3.y, explodedPositions.ic3.z);
      ic3Group.rotation.set(explodedPositions.ic3.rx, explodedPositions.ic3.ry, explodedPositions.ic3.rz);

      capGroup.position.y = explodedPositions.cap.y;
      transistorGroup.position.y = explodedPositions.transistor.y;
      connGroup.position.y = explodedPositions.conn.y;
    }
    applyExplodedState();

    // -------------------------------------------------------------------------
    // 9. DYNAMIC LEADER LINES & 2D SCREEN PROJECTION
    // -------------------------------------------------------------------------
    const lines = {
      mcu: document.getElementById('lineMcu'),
      ic1: document.getElementById('lineIc1'),
      ic2: document.getElementById('lineIc2'),
      cap: document.getElementById('lineCap'),
      transistor: document.getElementById('lineTransistor'),
      conn: document.getElementById('lineConnector')
    };

    const labels = {
      mcu: document.getElementById('labelMcu'),
      ic1: document.getElementById('labelIc1'),
      ic2: document.getElementById('labelIc2'),
      cap: document.getElementById('labelCap'),
      transistor: document.getElementById('labelTransistor'),
      conn: document.getElementById('labelConnector')
    };

    const targetObjects = {
      mcu: mcuGroup,
      ic1: ic1Group,
      ic2: ic2Group,
      cap: cap1,
      transistor: q2,
      conn: usbHousing
    };

    // Project 3D coordinate to Stage 2D pixels
    const projVector = new THREE.Vector3();
    function updateLeaderLines() {
      const stageRect = stage.getBoundingClientRect();
      const sWidth = stageRect.width;
      const sHeight = stageRect.height;

      Object.keys(lines).forEach(key => {
        const line = lines[key];
        const label = labels[key];
        const obj = targetObjects[key];

        if (!line || !label || !obj) return;

        // Get world coordinate of 3D object
        obj.getWorldPosition(projVector);
        // Project to normalized device coords [-1, 1]
        projVector.project(camera);

        // Convert to stage pixels
        const screenX = (projVector.x * 0.5 + 0.5) * sWidth;
        const screenY = (-(projVector.y * 0.5) + 0.5) * sHeight;

        // Get label center or anchor point
        const labelRect = label.getBoundingClientRect();
        // Point to nearest edge of the label card
        const labelX = (labelRect.left - stageRect.left) + (screenX < (labelRect.left - stageRect.left) ? 0 : labelRect.width);
        const labelY = (labelRect.top - stageRect.top) + (labelRect.height / 2);

        line.setAttribute('x1', screenX);
        line.setAttribute('y1', screenY);
        line.setAttribute('x2', labelX);
        line.setAttribute('y2', labelY);
      });
    }

    // -------------------------------------------------------------------------
    // 10. GSAP SCROLLTRIGGER SCENE ORCHESTRATION (4 Stages)
    // -------------------------------------------------------------------------
    const stageIndicator = document.getElementById('pcbStageIndicator');
    const stageName = document.getElementById('pcbStageName');
    const dots = document.querySelectorAll('.stage-step-dot');
    const completionCard = document.getElementById('pcbCompletionCard');
    const labelsOverlay = document.getElementById('pcbLabelsOverlay');
    const leaderLinesSvg = document.getElementById('pcbLeaderLines');

    function setStageUI(stepNum, name) {
      if (stageName) stageName.textContent = name;
      dots.forEach(d => {
        const num = parseInt(d.getAttribute('data-step'), 10);
        d.classList.toggle('active', num <= stepNum);
      });
    }

    // Timeline proxy object for smooth scrubbing
    const pcbTimelineState = {
      // Camera
      camX: 0, camY: 11, camZ: 17,
      // Board rotation
      boardRotX: 0.42, boardRotY: -0.45, boardRotZ: 0.15,
      // Assembly progress: 0 = fully exploded, 1 = fully assembled
      assemblyProgress: 0,
      // Label/line opacity
      labelsAlpha: 1,
      // Completion card opacity
      completionAlpha: 0
    };

    if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
      gsap.registerPlugin(ScrollTrigger);

      // Create master scrubbing timeline pinned to container
      const pcbMasterTL = gsap.timeline({
        scrollTrigger: {
          trigger: section,
          start: 'top top',
          end: '+=2400',
          pin: stage,
          scrub: 0.8,
          anticipatePin: 1,
          onUpdate: (self) => {
            const p = self.progress;

            // Update UI stage indicator based on scroll progress
            if (p < 0.25) {
              setStageUI(1, 'Stage 1: Exploded View');
            } else if (p < 0.50) {
              setStageUI(2, 'Stage 2: Approach');
            } else if (p < 0.80) {
              setStageUI(3, 'Stage 3: Assembly');
            } else {
              setStageUI(4, 'Stage 4: Completion');
            }
          }
        }
      });

      // -----------------------------------------------------------------------
      // STAGE A -> B: EXPLODED VIEW -> APPROACH (0% to 35%)
      // Camera zooms closer, board re-orients slightly for inspection
      // -----------------------------------------------------------------------
      pcbMasterTL.to(pcbTimelineState, {
        camX: -1.0,
        camY: 8.5,
        camZ: 13.5,
        boardRotX: 0.38,
        boardRotY: -0.28,
        boardRotZ: 0.08,
        duration: 1.2,
        ease: 'power1.inOut'
      }, 0);

      // -----------------------------------------------------------------------
      // STAGE B -> C: APPROACH -> ASSEMBLY (35% to 75%)
      // Components descend smoothly into mounting pads, labels retract
      // -----------------------------------------------------------------------
      pcbMasterTL.to(pcbTimelineState, {
        assemblyProgress: 1,
        labelsAlpha: 0,
        camX: 0.5,
        camY: 7.2,
        camZ: 11.8,
        boardRotX: 0.32,
        boardRotY: 0.05,
        boardRotZ: -0.02,
        duration: 1.5,
        ease: 'power2.inOut'
      }, 1.0);

      // -----------------------------------------------------------------------
      // STAGE C -> D: ASSEMBLY -> COMPLETION (75% to 100%)
      // Reveal close-up angle of finished board + introduce completion CTA card
      // -----------------------------------------------------------------------
      pcbMasterTL.to(pcbTimelineState, {
        camX: 2.2,
        camY: 5.6,
        camZ: 9.8,
        boardRotX: 0.28,
        boardRotY: 0.35,
        boardRotZ: -0.05,
        completionAlpha: 1,
        duration: 1.0,
        ease: 'power1.out'
      }, 2.4);
    } else {
      // Fallback if GSAP is not available: show assembled board
      pcbTimelineState.assemblyProgress = 1;
      pcbTimelineState.labelsAlpha = 0;
      pcbTimelineState.completionAlpha = 1;
    }

    // -------------------------------------------------------------------------
    // 11. SUBTLE MOUSE PARALLAX TILT
    // -------------------------------------------------------------------------
    let mouseX = 0;
    let mouseY = 0;
    let targetMouseX = 0;
    let targetMouseY = 0;

    window.addEventListener('mousemove', (e) => {
      targetMouseX = (e.clientX / window.innerWidth - 0.5) * 0.15;
      targetMouseY = (e.clientY / window.innerHeight - 0.5) * 0.15;
    });

    // -------------------------------------------------------------------------
    // 12. MAIN ANIMATION & RENDER LOOP
    // -------------------------------------------------------------------------
    let animFrameId;
    function renderLoop() {
      animFrameId = requestAnimationFrame(renderLoop);

      // Smooth mouse easing
      mouseX += (targetMouseX - mouseX) * 0.06;
      mouseY += (targetMouseY - mouseY) * 0.06;

      // Update camera position from timeline + mouse parallax
      camera.position.x = pcbTimelineState.camX + mouseX * 2.0;
      camera.position.y = pcbTimelineState.camY - mouseY * 1.5;
      camera.position.z = pcbTimelineState.camZ;
      camera.lookAt(0, 0, 0);

      // Update PCB Master Group rotation from timeline + mouse
      pcbMasterGroup.rotation.x = pcbTimelineState.boardRotX + mouseY * 0.5;
      pcbMasterGroup.rotation.y = pcbTimelineState.boardRotY + mouseX * 0.8;
      pcbMasterGroup.rotation.z = pcbTimelineState.boardRotZ;

      // Update component heights based on assemblyProgress (0 = exploded, 1 = mounted)
      const prog = pcbTimelineState.assemblyProgress;
      const inv = 1 - prog;

      // MCU Group
      mcuGroup.position.y = mountedPositions.mcu.y + (explodedPositions.mcu.y - mountedPositions.mcu.y) * inv;
      mcuGroup.rotation.x = explodedPositions.mcu.rx * inv;
      mcuGroup.rotation.y = explodedPositions.mcu.ry * inv;
      mcuGroup.rotation.z = explodedPositions.mcu.rz * inv;

      // ICs
      ic1Group.position.y = mountedPositions.ic1.y + (explodedPositions.ic1.y - mountedPositions.ic1.y) * inv;
      ic1Group.rotation.x = explodedPositions.ic1.rx * inv;
      ic1Group.rotation.y = explodedPositions.ic1.ry * inv;

      ic2Group.position.y = mountedPositions.ic2.y + (explodedPositions.ic2.y - mountedPositions.ic2.y) * inv;
      ic2Group.rotation.x = explodedPositions.ic2.rx * inv;
      ic2Group.rotation.z = explodedPositions.ic2.rz * inv;

      ic3Group.position.y = mountedPositions.ic3.y + (explodedPositions.ic3.y - mountedPositions.ic3.y) * inv;
      ic3Group.rotation.x = explodedPositions.ic3.rx * inv;

      // Capacitors, Transistors, Connectors
      capGroup.position.y = explodedPositions.cap.y * inv;
      transistorGroup.position.y = mountedPositions.transistor.y + (explodedPositions.transistor.y - mountedPositions.transistor.y) * inv;
      connGroup.position.y = explodedPositions.conn.y * inv;

      // Update Overlays (Labels & SVG Lines opacity)
      if (labelsOverlay) {
        labelsOverlay.style.opacity = pcbTimelineState.labelsAlpha;
        labelsOverlay.style.pointerEvents = pcbTimelineState.labelsAlpha > 0.2 ? 'auto' : 'none';
      }
      if (leaderLinesSvg) {
        leaderLinesSvg.style.opacity = pcbTimelineState.labelsAlpha;
      }
      if (completionCard) {
        completionCard.style.opacity = pcbTimelineState.completionAlpha;
        completionCard.style.pointerEvents = pcbTimelineState.completionAlpha > 0.3 ? 'auto' : 'none';
        completionCard.style.transform = `translate(-50%, ${(1 - pcbTimelineState.completionAlpha) * 30}px)`;
      }

      // Update projected 2D leader lines if visible
      if (pcbTimelineState.labelsAlpha > 0.05) {
        updateLeaderLines();
      }

      renderer.render(scene, camera);
    }

    renderLoop();

    // -------------------------------------------------------------------------
    // 13. RESPONSIVE RESIZE LISTENER
    // -------------------------------------------------------------------------
    function onWindowResize() {
      const newWidth = container.clientWidth || window.innerWidth;
      const newHeight = container.clientHeight || 750;

      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();

      renderer.setSize(newWidth, newHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

      if (typeof ScrollTrigger !== 'undefined') {
        ScrollTrigger.refresh();
      }
    }

    window.addEventListener('resize', onWindowResize);

    // -------------------------------------------------------------------------
    // 14. INTERACTIVE DOCK CONTROLS (Stitch View Modes & Camera Presets)
    // -------------------------------------------------------------------------
    let currentMode = 'exploded';

    window.setViewMode = function (btn, mode) {
      currentMode = mode;
      
      // Update UI segmented buttons
      const track = btn.parentElement;
      if (track) {
        track.querySelectorAll('button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      }

      if (typeof gsap === 'undefined') return;

      if (mode === 'exploded') {
        gsap.to(pcbTimelineState, { assemblyProgress: 0, labelsAlpha: 1, completionAlpha: 0, duration: 1.2, ease: 'power2.out' });
        restoreOriginalMaterials();
      } else if (mode === 'assembly') {
        gsap.to(pcbTimelineState, { assemblyProgress: 1, labelsAlpha: 0, completionAlpha: 1, duration: 1.2, ease: 'power2.out' });
        restoreOriginalMaterials();
      } else if (mode === 'xray') {
        gsap.to(pcbTimelineState, { assemblyProgress: 0.5, labelsAlpha: 0.5, completionAlpha: 0, duration: 1.2, ease: 'power2.out' });
        applyXRayMaterials();
      } else if (mode === 'thermal') {
        gsap.to(pcbTimelineState, { assemblyProgress: 0.8, labelsAlpha: 0.2, completionAlpha: 0, duration: 1.2, ease: 'power2.out' });
        applyThermalMaterials();
      }
    };

    function restoreOriginalMaterials() {
      icBodyMaterial.transparent = false;
      icBodyMaterial.opacity = 1.0;
      icBodyMaterial.color.setHex(0x1c1e24);
      icBodyMaterial.emissive.setHex(0x000000);
      pcbBoardMesh.material.emissive.setHex(0x000000);
    }

    function applyXRayMaterials() {
      icBodyMaterial.transparent = true;
      icBodyMaterial.opacity = 0.38;
      icBodyMaterial.color.setHex(0x006687);
      icBodyMaterial.emissive.setHex(0x002233);
      pcbBoardMesh.material.emissive.setHex(0x00150a);
    }

    function applyThermalMaterials() {
      icBodyMaterial.transparent = false;
      icBodyMaterial.opacity = 1.0;
      icBodyMaterial.color.setHex(0xc2410c);
      icBodyMaterial.emissive.setHex(0x7c2d12);
      pcbBoardMesh.material.emissive.setHex(0x1e293b);
    }

    window.setCameraPreset = function (preset) {
      if (typeof gsap === 'undefined') return;
      if (preset === 'isometric') {
        gsap.to(camera.position, { x: 0, y: 11, z: 17, duration: 1.2, ease: 'power2.inOut', onUpdate: () => camera.lookAt(0, 0, 0) });
      } else if (preset === 'top2d') {
        gsap.to(camera.position, { x: 0, y: 22, z: 0.01, duration: 1.2, ease: 'power2.inOut', onUpdate: () => camera.lookAt(0, 0, 0) });
      } else if (preset === 'flythrough') {
        gsap.to(camera.position, { x: 5, y: 6, z: 9, duration: 1.5, ease: 'power2.inOut', onUpdate: () => camera.lookAt(0, 0.5, 0) });
      } else if (preset === 'snapshot') {
        takeHighResSnapshot();
      }
    };

    function takeHighResSnapshot() {
      renderer.render(scene, camera);
      const dataURL = renderer.domElement.toDataURL('image/png');
      const a = document.createElement('a');
      a.href = dataURL;
      a.download = 'CircuitSense-3D-PCB-Snapshot.png';
      a.click();
    }

    // Initial leader line layout calculation
    setTimeout(updateLeaderLines, 100);
  }
})();
