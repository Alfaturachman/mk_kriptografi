# Reversible watermarking for medical images using ROI-based tamper localization and recovery *

**Aulia Arham**, **Teguh Bharata Adji**, **Syukron Abu Ishaq Alfarozi**, **Hanung Adi Nugroho***

Department of Electrical and Information Engineering, Faculty of Engineering, Universitas Gadjah Mada, Jl. Grafika No. 2 Kampus UGM, Yogyakarta, 55281, Indonesia

---

## Abstract

Medical image watermarking has received increasing attention in recent years for securing patient information and ensuring image integrity. To prevent diagnostic errors, data embedding must be fully reversible, and the watermarking scheme must detect and restore tampered regions. This paper proposes a reversible watermarking technique that supports high-capacity data embedding while preserving diagnostic quality and enabling authentication and recovery. The image is divided into three regions: the ROI, where patient records are reversibly embedded using a multi-layer difference expansion scheme; the RONI, where semi-fragile 2D-DE embedding enables tamper localization and recovery; and the border region, which stores auxiliary information using simple, non-robust LSB encoding that does not affect diagnostic content. Experimental results on MRI, ultrasound, and X-ray images show that the method can embed up to 10 kB of patient data using only 12% of the image as ROI, while maintaining high visual quality with average PSNR values above 38 dB and SSIM values close to 1.00. The watermarked images are perfectly reconstructed after extraction, except for the nonreversible border. A clear security and threat model is defined, assuming attackers may manipulate images, add mild noise, or structurally alter content. Under this model, the scheme successfully detects and localizes tampered regions through hash comparison and block analysis, and recovers corrupted ROI areas with quality improvements of up to +28.14 dB. The proposed method ensures full reversibility and reliable extraction of patient information when the ROI is not tampered, while lossy compression-based recovery provides visually meaningful restoration for tampered regions.

## Keywords

- Medical image watermarking
- Reversible embedding
- Tamper detection
- Tampered area localization
- Image recovery
- Difference expansion

**Dataset link:** https://github.com/4rh4m/Reversible-Medical-Image-Watermarking

---

## 1. Introduction

The swift progression of internet technology has enabled universal access to digital images. By utilizing image processing, digital data can be conveniently modified, altered, and disseminated [1-3]. The ease of manipulating images highlights the critical need for image authentication in applications where verifying the authenticity and integrity of images is crucial, especially in medical, military, and forensic imaging [4-6].

Medical images are visual depictions of specific organs or tissues in a patient, used primarily for diagnosis or detecting diseases. Medical images can be acquired through various imaging technologies, such as Magnetic Resonance Imaging (MRI), Computerized Radiography (CR), Ultrasound (US), Computer Tomography (CT), among others [1,7,8], which are stored in hospital databases. The images can be transferred over internet communication networks between healthcare facilities and data centers. It is important to properly manage patient records and medical images to avoid mishandling and data loss, increase utilization, improve communication channel efficiency, and reduce storage size.

Ensuring the security of medical images is a critical issue, especially when transmitting images and patient records over the internet, as it is vital to protect their integrity [9-12]. Cryptographic techniques are commonly applied for this purpose. Numerous studies [9,10,13-18] have explored the integration of cryptographic schemes with watermarking to safeguard image content. Algorithms such as AES, DES, RSA, MD5, SHA-256, and chaotic maps are widely used to prevent tampering, as the encrypted data is difficult to alter without detection. However, these methods do not provide localization or recovery of the tampered regions within the image.

Image authentication methods are generally employed for purposes such as copyright protection, ownership verification, and tamper detection [19]. Broadly, these methods fall into two categories: hard and soft authentication [1]. Hard authentication, including techniques like Message Authentication Codes (MACs) [1,20], offers robust integrity checks, as demonstrated in several studies [17,21]. On the other hand, soft authentication, such as digital watermarking [1,22], has been explored in research focusing on image ownership and content validation [9,13,14,16,23-25]. Both types of methods can detect when an image has been tampered with, but they cannot determine the specific location of the tampering or recover the original image [1].

Image watermarking methods have been proposed by various researchers [10,19,21,22,26,27] to identify tampered areas in images. These methods not only determine if an image has been tampered with but also identify where the tampering occurred and can pinpoint the specific areas. Other researchers [28-33] have suggested watermarking methods that enable the identification of tampered areas and image recovery. However, such methods often rely on embedding strategies that may degrade the visual quality of the original image. To address this concern, reversible watermarking schemes have been proposed [4,5,34-50], which allow the original image to be completely restored after watermark extraction, albeit without tamper localization features. More recent efforts [2,51] have introduced reversible watermarking techniques that incorporate tamper detection mechanisms, enabling both image recovery and precise identification of altered areas.

The method proposed in this study seeks to address the limitations of current approaches by offering a reversible watermarking scheme tailored to medical images, capable of detecting tampering, recovering affected areas, and embedding patient data. As noted by AlQershi and Khoo [52], effective watermarking techniques for medical images should ensure both integrity verification and recovery, while also supporting the embedding of electronic patient records (EPR) to reduce storage and transmission costs. Three main categories of such methods can be identified: those focused on tamper detection and recovery [1,53,54], those aimed at embedding patient records [55], and hybrid approaches that combine both objectives [41,52,56,57]. Coatrieux et al. [58] further classify watermarking algorithms into methods that embed information outside diagnostic regions, reversible schemes, and algorithms that minimize distortion using basic techniques such as least significant bit (LSB) embedding and lossless compression [21].

Contemporary research continues to explore strategies that balance image fidelity and security. Approaches involving the separation of the image into a Region of Interest (ROI) and Region of Non-Interest (RONI) are commonly employed to ensure reversibility and protect sensitive content [59-61]. Fragile watermarks are typically used in ROI areas for integrity checks, while robust watermarks serve copyright protection purposes [61]. Some techniques utilize compression algorithms like LZW to embed recovery information [60], while others leverage prediction-based methods to avoid location map overhead [61]. Advanced schemes incorporate encryption of patient records and adaptive key generation for enhanced security [62]. These approaches demonstrate high imperceptibility, robustness against various attacks, and low computational costs [60,62]. Overall, these techniques aim to ensure the confidentiality, integrity, and authenticity of medical images in e-healthcare environments.

This study proposes a new approach for reversible medical image watermarking that integrates both authentication and data hiding. The images are divided into three parts. The first part is the region of interest (ROI), where patient records and a hash message of the ROI are reversibly embedded using the method proposed by Arham et al. [4]. The second part is the region of non-interest (RONI), where data for tamper detection, recovery, and the embedding map from the ROI are stored, using the scheme suggested by Al-Qershi and Khoo [42]. The third part is the border area, which is used for embedding the coordinates of the selected ROI and the embedding map of the RONI using the Least Significant Bit (LSB) method. This research aims to develop a technique that can authenticate medical images, detect and locate tampered areas, and restore the image. Additionally, it facilitates the storage of patient records, thereby reducing storage and transmission costs.

<p align="center"><b>Fig. 1.</b> The Quad configuration in the image [37].</p>

<p align="center"><b>Fig. 2.</b> Transformed the pixels into vector (a) left-to-right scanning, (b) top-to-bottom scanning [55].</p>

## 2. Related works

This section explains the various schemes that are used in the proposed scheme. These include DE, DE of Quad, Reduced DE, Improved RDE, multiple-layer data hiding, and two-dimensional DE (2D-DE).

### 2.1. Difference expansion (DE)

Tian [63] introduced the DE scheme, a method that involves embedding data by utilizing the difference between two adjacent pixels while keeping the average value unchanged. If $p_1$ and $p_2$ are pairs of adjacent pixels in an 8-bit grayscale image, then Eq. (1) calculates the difference $d$ between the two pixels and their mean value $\bar{x}$:

$$
\bar{x} = \left\lfloor \frac{p_1 + p_2}{2} \right\rfloor, \quad d = p_1 - p_2
$$

Data embedding involves expanding the pixel difference $d$ by adding the payload bit $b \in \{0,1\}$, producing the expanded difference $d'$:

$$
d' = 2 \times d + b
$$

Here, $d'$ represents the modified pixel difference after expansion and bit embedding.

The new pixel values, $p_1'$ and $p_2'$, are then obtained while keeping the average value unchanged:

$$
p_1' = \bar{x} + \left\lfloor \frac{d' + 1}{2} \right\rfloor, \quad p_2' = \bar{x} - \left\lfloor \frac{d'}{2} \right\rfloor
$$

To ensure that the modified pixel values remain in the valid grayscale range $[0,255]$, the expanded difference $d'$ must satisfy:

$$
\left\{ \begin{array}{ll}
|d'| \leq 2 \times (255 - \bar{x}), & \text{if } 128 \leq \bar{x} \leq 255 \\
|d'| \leq 2 \times \bar{x} + 1, & \text{if } 0 \leq \bar{x} \leq 127
\end{array} \right.
$$

For data extraction and recovery, the stego pixel pair $(p_1', p_2')$ is first used to recompute the average $\bar{x}$ and the expanded difference $d'$:

$$
\bar{x} = \left\lfloor \frac{p_1' + p_2'}{2} \right\rfloor, \quad d' = p_1' - p_2'
$$

The embedded bit is then obtained as:

$$
b = d' \bmod 2
$$

The original difference $d$ is recovered as:

$$
d = \left\lfloor \frac{d'}{2} \right\rfloor
$$

Finally, the original pixel values $(p_1, p_2)$ are reconstructed using:

$$
p_1 = \bar{x} + \left\lfloor \frac{d + 1}{2} \right\rfloor, \quad p_2 = \bar{x} - \left\lfloor \frac{d}{2} \right\rfloor
$$

Although theoretically capable of embedding up to 0.5 bits per pixel (bpp), DE's primary limitation is its dependence on an embedding map, which reduces its effective capacity.

### 2.2. DE of Quad

The DE of Quad method divides an image into $2 \times 2$ blocks, converting each block into a four-pixel vector [37]. Pixels are scanned either left-to-right or top-to-bottom as shown in Fig. 2, and the block configuration is illustrated in Fig. 1. Each vector $q = (p_0, p_1, p_2, p_3)$ is transformed using:

$$
\left\{ \begin{array}{l}
d_0 = \left\lfloor \frac{p_0 + p_1 + p_2 + p_3}{4} \right\rfloor \\
d_1 = p_1 - p_0 \\
d_2 = p_2 - p_1 \\
d_3 = p_3 - p_2
\end{array} \right.
$$

Reconstruction of the original block is achieved through:

$$
\left\{ \begin{array}{l}
p_0 = d_0 - \left\lfloor \frac{d_1 + d_2 + d_3}{4} \right\rfloor \\
p_1 = d_1 + p_0 \\
p_2 = d_2 + p_1 \\
p_3 = d_3 + p_2
\end{array} \right.
$$

To embed data bits $b_1, b_2$, and $b_3$, two strategies are used depending on overflow and underflow risks:

$$
\left\{ \begin{array}{l}
d_1' = 2 \times d_1 + b_1 \\
d_2' = 2 \times d_2 + b_2 \\
d_3' = 2 \times d_3 + b_3
\end{array} \right.
$$

$$
\left\{ \begin{array}{l}
d_1' = 2 \times \left\lfloor \frac{d_1}{2} \right\rfloor + b_1 \\
d_2' = 2 \times \left\lfloor \frac{d_2}{2} \right\rfloor + b_2 \\
d_3' = 2 \times \left\lfloor \frac{d_3}{2} \right\rfloor + b_3
\end{array} \right.
$$

For valid embedding, the following conditions must hold:

$$
\left\{ \begin{array}{l}
0 \leq d_0 - \left\lfloor \frac{d_1' + d_2' + d_3'}{4} \right\rfloor \leq 255 \\
0 \leq d_1' + p_0 \leq 255 \\
0 \leq d_2' + p_1 \leq 255 \\
0 \leq d_3' + p_2 \leq 255
\end{array} \right.
$$

The updated pixels $p_0'$ to $p_3'$ are reconstructed as:

$$
\left\{ \begin{array}{l}
p_0' = p_0 \\
p_1' = d_1' + p_0' \\
p_2' = d_2' + p_1' \\
p_3' = d_3' + p_2'
\end{array} \right.
$$

This scheme increases the embedding capacity to 0.75 bpp compared to standard DE.

### 2.3. Reduced DE (RDE)

Liu et al. [63] developed the RDE approach to limit large pixel variations introduced by conventional DE. In RDE, only pixels with values greater than 1 are altered, while others remain unchanged:

$$
d_i' = \begin{cases} d_i, & \text{if } d_i < 2 \\ d_i - 2^{\log_2 |d_i| - 1}, & \text{if } d_i \geq 2 \end{cases}
$$

A location map (LM) stores which differences were reduced. The original differences are reconstructed using:

$$
d_i = \begin{cases} d_i' + 2^{\log_2 |d_i'| - 1}, & \text{if } LM = 0 \\ d_i' + 2^{\log_2 |d_i'|}, & \text{if } LM = 1 \end{cases}
$$

### 2.4. Improved RDE

Yi et al. [64] introduced an enhancement to the Reduced Difference Expansion (RDE) technique with the goal of minimizing pixel differences before the embedding process. This modification, known as Improved RDE (IRDE), reduces pixel differences more effectively, which can lead to better visual quality and increased embedding capacity. The IRDE approach adjusts the pixel values according to specific ranges, as described in Eq. (17), and calculates an intermediate parameter $n$ using Eq. (18).

$$
d_i' = \begin{cases} d_i - 2^{\log_2 |d_i| - 1}, & \text{if } 2 \times 2^{n-1} \leq d_i \leq 3 \times 2^{n-1} - 1 \\ d_i - 2^{\log_2 |d_i|}, & \text{if } 3 \times 2^{n-1} \leq d_i \leq 4 \times 2^{n-1} - 1 \end{cases}, \quad n = \left\lfloor 2^{\log_2 |d_i|} \right\rfloor
$$

The creation of a location map (LM) determines whether a reduction operation has been applied. This information is critical for restoring the image and is computed using Eq. (19).

$$
LM = \begin{cases} 0, & \text{if } 2 \times 2^{n-1} \leq d_i \leq 3 \times 2^{n-1} - 1 \\ 1, & \text{if } 3 \times 2^{n-1} \leq d_i \leq 4 \times 2^{n-1} - 1 \end{cases}
$$

Using the location map, the original values of the pixel differences are reconstructed by applying Eq. (20).

$$
d_i = \begin{cases} d_i' + 2^{\log_2 |d_i'| + 1}, & \text{if } LM = 1 \\ d_i' + 2^{\log_2 |d_i'|}, & \text{if } LM = 0 \end{cases}
$$

### 2.5. Multiple-layer data hiding

Multiple-layer data hiding refers to embedding data in successive rounds to increase capacity. This strategy is only feasible with reversible data hiding techniques, ensuring that the original image can be completely restored.

#### 2.5.1. Multiple-layer data hiding based on DE

The method involves repetitive use of the DE scheme [65], which expands pixel differences to accommodate additional data. However, repeating DE embedding causes visual degradation. To address this, Lou et al. [55] integrated RDE to minimize distortion. The data embedding is applied layer-by-layer with horizontal, vertical, and alternating scanning directions. If $k$ layers are used in an $m \times n$ image, the embedding capacity becomes $m \times n/2 \times k$ bits.

#### 2.5.2. Multiple-layer data hiding based on DE of Quad

This approach employs the DE of Quad technique proposed by Alattar [37], adapted for multiple-layer embedding. Arham et al. [4] suggested using IRDE to enhance quality and increase capacity. As shown in Fig. 3, data is embedded in four layers with distinct scanning patterns.

In each layer, different pixel orderings (e.g., $q_0 = (p_0, p_1, p_2, p_3)$ in the first layer) are used to derive differences (d vectors) via Eqs. (21) to (28). These enable reconstruction after embedding by applying inverse operations.

$$
\left\{ \begin{array}{l}
d_1 = p_1 - p_0 \\
d_2 = p_2 - p_1 \\
d_3 = p_3 - p_2 \\
p_0 = v_0 - \left\lfloor \frac{3d_1 + 2d_2 + d_3}{4} \right\rfloor \\
p_1 = d_1 + p_0 \\
p_2 = d_2 + p_1 \\
p_3 = d_3 + p_2
\end{array} \right.
$$

<p align="center"><b>Fig. 3.</b> Generate vectors to 4 layers [4].</p>

<p align="center"><b>Fig. 4.</b> 2D-DE for Smooth Block [1].</p>

$$
\left\{ \begin{array}{l}
d_1 = p_3 - p_1 \\
d_2 = p_0 - p_3 \\
d_3 = p_2 - p_0
\end{array} \right.
$$

$$
\left\{ \begin{array}{l}
p_1 = d_0 - \left\lfloor \frac{3d_1 + 2d_2 + d_3}{4} \right\rfloor \\
p_3 = d_1 + p_1 \\
p_0 = d_2 + p_3 \\
p_2 = d_3 + p_0
\end{array} \right.
$$

$$
\begin{array}{l}
d_1 = p_3 - p_2 \\
d_2 = p_0 - p_3 \\
d_3 = p_1 - p_0
\end{array}
$$

$$
\begin{array}{l}
p_2 = d_0 - \left\lfloor \frac{3d_1 + 2d_2 + d_3}{4} \right\rfloor \\
p_3 = d_1 + p_2 \\
p_0 = d_2 + p_3 \\
p_1 = d_3 + p_0
\end{array}
$$

$$
\begin{array}{l}
d_1 = p_1 - p_3 \\
d_2 = p_2 - p_1 \\
d_3 = p_0 - p_2
\end{array}
$$

$$
\left\{ \begin{array}{l}
p_3 = d_0 - \left\lfloor \frac{3d_1 + 2d_2 + d_3}{4} \right\rfloor \\
p_1 = d_1 + p_3 \\
p_2 = d_2 + p_1 \\
p_0 = d_3 + p_2
\end{array} \right.
$$

The sequential application of all layers ensures non-overlapping use of pixel differences. The same layer order must be used during extraction to reconstruct the embedded data and restore the image.

### 2.6. Two-dimensional DE (2D-DE)

The 2D-DE scheme, introduced by Al-Qershi and Khoo [42], is an enhancement over Chiang's method [1], allowing more data to be embedded in $4 \times 4$ pixel blocks by applying a 2-level Discrete Wavelet Transform (DWT). The process is illustrated in Fig. 4.

The image is first decomposed via horizontal and vertical operations using Eqs. (29)-(32), producing four frequency sub-bands (LL1, LH1, HL1, HH1) as shown in Fig. 5. This process is repeated on the LL1 sub-band for 2-level DWT.

$$
P_{ij} = \left[ \frac{I_{i,2j} - I_{i,2j+1}}{2} \right], \quad \text{when } 0 \leq j < \frac{n}{2}
$$

$$
P_{ij} = \left[ \frac{I_{i,2(j - n/2)} - I_{i,2(j - n/2)+1}}{2} \right], \quad \text{when } \frac{n}{2} \leq j < n
$$

<p align="center"><b>Fig. 5.</b> (a) 1-level DWT and (b) 2-level DWT [42].</p>

$$
Q_{ij} = \left[ \frac{P_{2i,j} - P_{2i+1,j}}{2} \right], \quad \text{when } 0 \leq i < \frac{n}{2}
$$

$$
Q_{ij} = \left[ \frac{P_{2(i - n/2),j} - P_{2(i - n/2)+1,j}}{2} \right], \quad \text{when } \frac{n}{2} \leq i < n
$$

Chiang's method embeds data only in smooth blocks with zero values (except one corner). Although simple and efficient, it is not ideal for images with limited smoothness.

In contrast, the 2D-DE method allows embedding in both smooth and non-smooth regions. It embeds 16 bits in each $4 \times 4$ block by modifying wavelet coefficients in LH1, HL1, and HH1 sub-bands using Eqs. (33) and (34):

$$
q' = q \times 2 + b, \quad \text{for LH1 and HL1}
$$

$$
q' = q \times 4 + b_2 b_1, \quad \text{for HH1}
$$

Here, $q$ is a coefficient and $b, b_1, b_2$ are data bits. The scheme is highly efficient and suitable for various image types.

## 3. Proposed method

The proposed medical image watermarking scheme is designed to ensure integrity, authentication, and full reversibility of medical images. It addresses key limitations of previous approaches by providing Tamper Detection (TD), Tamper Localization (TL), and Tamper Recovery (TR), while also supporting the secure and reversible embedding of patient-related information (ED), as illustrated in Fig. 6.

To achieve this, the input medical image is segmented into three primary regions, as shown in Fig. 7:

- **Region of Interest (ROI):** contains diagnostically significant structures.
- **Region of Non-Interest (RONI):** includes non-critical background areas.
- **Border region:** used for embedding secondary data such as coordinates and embedding maps.

This section outlines how different types of data are embedded across the three regions using techniques optimized for the characteristics of each area. For the ROI, patient records and a hash message are embedded using a multi-layer reversible embedding scheme based on [4], chosen for its high capacity and ability to fully restore the diagnostic content without distortion. For the RONI, data supporting tamper localization and recovery along with the ROI embedding map are embedded using the two-dimensional Difference Expansion (2D-DE) method based on [42]. This method provides a good balance between capacity, imperceptibility, and reversibility in non-critical regions.

The coordinates of the ROI and the RONI embedding map are then stored within the border region using a Least Significant Bit (LSB) embedding technique. LSB is employed here because the border does not contain diagnostic information and can tolerate slight modifications, while offering high capacity with low computational cost.

<p align="center"><b>Fig. 6.</b> Overview of the proposed method.</p>

<p align="center"><b>Fig. 7.</b> Segmentation of the host image into ROI, RONI, and border regions.</p>

In addition, this section details the preprocessing and watermark construction, followed by the region-specific embedding and extraction procedures, as well as the mechanisms for Tamper Detection, Localization, and Recovery (TDLR) of the modified regions to ensure complete integrity verification and restoration of the medical image.

### 3.1. Preprocessing and watermark creation

This stage involves image preprocessing and the generation of all watermark components. The input image is first segmented into the ROI, RONI, and Border regions. The ROI is manually delineated by authorized physicians using polygon-based contours in accordance with standard radiological guidelines to ensure that all diagnostically relevant structures are fully included. To improve reproducibility, the ROI mask is independently verified by a second physician, resulting in consistent boundaries with minimal inter-rater variation. The polygon coordinates are then losslessly encoded and embedded into the Border region to guarantee exact ROI reconstruction during extraction. A small sensitivity check indicates that slight boundary deviations ($\pm 1$-2 pixels) do not significantly affect tamper localization or recovery. Finally, preprocessing is applied to obtain the processed ROI suitable for reversible embedding.

Seven watermark components are generated in this stage: (1) patient information; (2) ROI hash generated using the SHA-256 algorithm; (3) compressed ROI; (4) compressed mean values of $8 \times 8$ ROI blocks; (5) compressed ROI embedding map; (6) ROI coordinate data; and (7) compressed RONI embedding map. These components are grouped into three watermark sets based on their purpose and corresponding embedding region.

The first two components form watermark1 ($W_1$), which is embedded into the ROI to ensure authentication and tamper detection. The next three components comprise watermark2 ($W_2$), embedded into the RONI to enable tamper localization and recovery. The final two components constitute watermark3 ($W_3$), embedded into the Border region to store ROI-related metadata and to facilitate correct extraction of data embedded within the RONI.

Two compression techniques are employed: the ROI is compressed using the JPEG 2000 standard to preserve image quality while achieving efficient compression, whereas the remaining components, namely the block mean values, the ROI embedding map, and the RONI embedding map, are compressed using Huffman coding to reduce redundancy and minimize auxiliary data size.

#### 3.1.1. Watermark embedded in the ROI

The watermark embedded in the ROI, denoted as $W_1$, consists of the compressed patient information $D$ and a hash message $Hash_1$ computed from the ROI using SHA-256. These elements support data integrity verification and secure reversible embedding of patient-related information. The structure of $W_1$ is shown in Fig. 8.

<p align="center"><b>Fig. 8.</b> Structure of watermark embedded in the ROI.</p>

#### 3.1.2. Watermark embedded in the RONI

The watermark embedded within the RONI region, denoted as $W_2$, consists of the compressed ROI image $ROI_{comp}$, the compressed mean values of $8 \times 8$ ROI blocks $m_{comp}$, and the compressed ROI embedding map $EM_{1_{comp}}$. Each component is accompanied by its respective size metadata to ensure accurate extraction and decoding. The organization of $W_2$ is depicted in Fig. 9.

<p align="center"><b>Fig. 9.</b> Structure of watermark embedded in the RONI.</p>

#### 3.1.3. Watermark embedded in the border

The watermark inserted into the Border region, denoted as $W_3$, contains the ROI coordinate data $(P, MP)$, size metadata related to $W_2$, the compressed RONI embedding map $EM_{2_{comp}}$, and additional supporting metadata. This information is essential for guiding watermark extraction, tamper verification, and complete image reconstruction. The structure of $W_3$ is shown in Fig. 10.

<p align="center"><b>Fig. 10.</b> Structure of watermark embedded in the border region.</p>

### 3.2. Embedding procedure

The embedding procedure begins with manual delineation of the Region of Interest (ROI) by an authorized radiologist, who specifies the ROI polygon coordinates $P$. These coordinates are recorded in a matrix $MP$ for subsequent use. The host image is partitioned into $8 \times 8$ pixel blocks and segmented into three regions ROI, RONI, and Border based on the spatial relation to the ROI polygon.

Next, the ROI is compressed using the JPEG 2000 standard to produce $ROI_{comp}$, which serves as recovery data in the event of tampering. A lossy JPEG 2000 compression is intentionally applied to reduce the size of recovery data while preserving diagnostic reversibility through the use of an embedding map. For tamper localization, the mean value $m$ of each $8 \times 8$ ROI block is computed and stored. All hashing operations are performed using the SHA-256 algorithm: the ROI hash $Hash_1$ is computed from the processed ROI and will be used for authentication and tamper detection.

The compressed patient record $D$ and $Hash_1$ are concatenated to form the first watermark $W_1$. The ROI is then subdivided into $2 \times 2$ pixel quads and $W_1$ is embedded into these quads using a multi-layer quad-based Difference Expansion (DE) scheme. The embedding loop continues until all bits of $W_1$ are embedded, and an embedding map $EM_1$ is produced to record which pixels/quads were modified.

To reduce overhead, the block mean values $m$ and the embedding map $EM_1$ are compressed using Huffman coding, resulting in $m_{comp}$ and $EM_{1_{comp}}$. The second watermark $W_2$ is formed by concatenating $ROI_{comp}$, $m_{comp}$, and $EM_{1_{comp}}$.

The RONI is partitioned into $4 \times 4$ blocks. The watermark $W_2$ is embedded into these RONI blocks using the two-dimensional Difference Expansion (2D-DE) method, yielding an embedding map $EM_2$. The map $EM_2$ is then compressed with Huffman coding to produce $EM_{2_{comp}}$.

Finally, the ROI polygon coordinates $(P, MP)$ and $EM_{2_{comp}}$ are concatenated to form the border watermark $W_3$, which is embedded into the image border using Least Significant Bit (LSB) substitution. The output of this stage is the fully watermarked image ready for storage or secure transmission.

The watermarked image can then be stored in a hospital database or transmitted to other healthcare institutions. The details of the watermark embedding process are presented in Algorithm 1 and illustrated in Fig. 11.

<p align="center"><b>Fig. 11.</b> Watermark embedding procedure of the proposed scheme.</p>

**Algorithm 1.** Watermark embedding process

*Require:* Medical image $I$, ROI polygon $P$, patient data $D$  
*Ensure:* Watermarked image $I_w$

1. Segment $I$ into ROI, RONI, and Border regions using polygon $P$.
2. Compute SHA-256 hash of ROI: $Hash_{ROI} \leftarrow SHA256(I_{ROI})$.
3. Compress ROI using JPEG2000: $ROI_{comp} \leftarrow JPEG2000\_Compress(I_{ROI})$.
4. Compute mean values of $8 \times 8$ ROI blocks: $m \leftarrow BlockMean(I_{ROI})$.
5. Form first watermark: $W_1 \leftarrow \{D, Hash_{ROI}\}$.
6. *ROI embedding (multi-stage reversible watermarking):* Embed $W_1$ into ROI using quad-based DE: $ROI_{emb}, EM_1 \leftarrow DE\_Quad(I_{ROI}, W_1)$.
7. Compress $m$ and $EM_1$ using Huffman: $m_{comp}, EM_{1_{comp}} \leftarrow Huffman(m, EM_1)$.
8. Form second watermark: $W_2 \leftarrow \{ROI_{comp}, m_{comp}, EM_{1_{comp}}\}$.
9. *RONI embedding:* Embed $W_2$ into RONI using 2D-DE: $RONI_{emb}, EM_2 \leftarrow DE\_2D(I_{RONI}, W_2)$.
10. Compress $EM_2$ using Huffman: $EM_{2_{comp}} \leftarrow Huffman(EM_2)$.
11. Form third watermark: $W_3 \leftarrow \{P, MP, size(W_2), EM_{2_{comp}}\}$.
12. *Border embedding:* Embed $W_3$ into Border using LSB substitution: $Border_{emb} \leftarrow LSB\_Embed(I_{Border}, W_3)$.
13. Combine embedded subregions: $I_w \leftarrow Merge(ROI_{emb}, RONI_{emb}, Border_{emb})$.
14. **return** $I_w$.

### 3.3. Extraction, tamper detection, localization, and recovery

The extraction process begins by retrieving the watermark data embedded in the border region. From this region, the ROI coordinates $(P, MP)$, the size information of $W_2$, and the compressed embedding map of the RONI $(EM_{2_{comp}})$ are extracted. After decompressing $EM_{2_{comp}}$ to obtain $EM_2$, the received image is segmented into ROI, RONI, and border regions following the same polygon-based segmentation used during embedding.

The RONI region is then divided into $4 \times 4$ blocks, and the second watermark $W_2$ is extracted using the inverse two-dimensional Difference Expansion (2D-DE) guided by $EM_2$. The extracted $W_2$ is decomposed into three components: the lossy-compressed ROI data $ROI_{comp}$, the compressed block means $m_{comp}$, and the compressed ROI embedding map $EM_{1_{comp}}$. These components are subsequently decompressed using Huffman decoding (for $m_{comp}$ and $EM_{1_{comp}}$) and JPEG2000 decompression (for $ROI_{comp}$), yielding the block mean values $m$ and the ROI embedding map $EM_1$.

Next, the ROI is divided into $2 \times 2$ pixel quads, and the first watermark $W_1$ is extracted from the ROI using the inverse quad-based DE technique guided by $EM_1$. The extracted watermark $W_1$ is separated into the patient information $D$ and the ROI hash value $Hash_1$. Using the reversible embedding map, a preliminary reconstruction of the ROI, denoted as $ROI_{rec}$, is performed.

Tamper detection is carried out by computing a new SHA-256 hash value $Hash_2$ from $ROI_{rec}$ and comparing it with the extracted hash $Hash_1$. If both hash values match, the ROI is declared authentic, meaning that no tampering has occurred. In this case, both the reconstructed ROI and the extracted patient data $D$ are valid, and the process terminates.

If the two hash values differ, tampering is detected, and the system proceeds to localize the modified regions. Localization is performed by comparing the recovered block means $m$ with the mean values $m_2$ computed from the corresponding $8 \times 8$ blocks of the reconstructed ROI $ROI_{rec}$. Any block where $m[b] \neq m_2[b]$ is marked as tampered, producing a block-level tamper map.

To recover tampered regions, the previously extracted lossy-compressed ROI data $ROI_{comp}$ is decompressed to obtain $ROI_{dec}$. For each block marked as tampered, the corresponding block within $ROI_{rec}$ is replaced with the matching block from $ROI_{dec}$, yielding a visually consistent but not bitwise identical restoration of the original ROI. Because this recovery relies on lossy data, the reconstructed ROI cannot match the original ROI at a pixel level, and therefore the extracted patient data $D$ cannot be guaranteed to remain intact when tampering occurs and recovery is required.

The final outputs of this process are the reconstructed image $I_{rec}$, the tamper localization map, and the patient data $D$. The value of $D$ is considered valid only when no tampering has been detected; otherwise it is flagged as unreliable due to lossy reconstruction. The details of watermark extraction, tamper detection, localization, and recovery are presented in Algorithm 2 and illustrated in Fig. 12.

**Algorithm 2.** Extraction, tamper detection, localization, and recovery (lossy ROI case)

*Require:* Watermarked image $I_w$  
*Ensure:* Restored image $I_{rec}$, patient data $D$ (if valid), tamper map $T$

1. *Extract $W_3$ and segment regions:* Extract $W_3 = \{P, MP, size(W_2), EM_{2_{comp}}\}$ from Border via LSB.
2. $EM_2 \leftarrow Huffman\_Decode(EM_{2_{comp}})$.
3. Segment $I_w$ into ROI, RONI, Border using $(P, MP)$.
4. *Extract $W_2$ from RONI:* $W_2 \leftarrow DE\_2D\_Extract(I_{RONI}, EM_2)$.
5. Parse $W_2 \rightarrow \{ROI_{comp}, m_{comp}, EM_{1_{comp}}\}$.
6. $m \leftarrow Huffman\_Decode(m_{comp})$.
7. $EM_1 \leftarrow Huffman\_Decode(EM_{1_{comp}})$.
8. *Extract $W_1$ from ROI:* $W_1 \leftarrow DE\_Quad\_Extract(I_{ROI}, EM_1)$.
9. Parse $W_1 \rightarrow \{D, Hash_1\}$.
10. Reconstruct preliminary ROI: $ROI_{rec} \leftarrow Reconstruct(I_{ROI}, EM_1)$.
11. *Tamper detection (lossy case):* $Hash_2 \leftarrow SHA256(ROI_{rec})$.
12. **if** $Hash_1 = Hash_2$ **then**
13. $T \leftarrow$ zero tamper map.
14. $I_{rec} \leftarrow Merge(ROI_{rec}, I_{RONI}, I_{Border})$.
15. **return** $I_{rec}, D, T$ *(D is valid only in the non-tampered case)*.
16. **end if**
17. *Tamper localization:* Compute $m_2 \leftarrow BlockMean(ROI_{rec})$.
18. **for** each ROI block index $b$ **do**
19. **if** $m[b] \neq m_2[b]$ **then** $T[b] \leftarrow 1$ **else** $T[b] \leftarrow 0$.
20. **end for**
21. *Recovery of tampered blocks (lossy recovery):* $ROI_{dec} \leftarrow JPEG2000\_Decompress(ROI_{comp})$.
22. **for** each block $b$ with $T[b] = 1$ **do** replace block $b$ in $ROI_{rec}$ with the corresponding block from $ROI_{dec}$.
23. $I_{rec} \leftarrow Merge(ROI_{rec}, I_{RONI}, I_{Border})$.
24. *(D is unreliable due to lossy reconstruction.)* **return** $I_{rec}, D_{invalid}, T$.

<p align="center"><b>Fig. 12.</b> The extraction of watermark, tamper detection, localization, and recovery.</p>

## 4. Result and discussion

### 4.1. Dataset and experimental setup

The proposed algorithm is evaluated in terms of embedding quality, capacity, confidentiality, security, robustness, reversibility, and tamper detection/localization and recovery performance. A total of 30 grayscale medical images are used in the experiments, consisting of 10 MRI, 10 ultrasound (US), and 10 X-ray images, with sample images shown in Fig. 13. The method is tested using multiple ROI sizes — 4%, 8%, and 12% of the image area as illustrated in Fig. 14. Patient records of sizes 2 kB, 6 kB, and 10 kB are embedded within the ROI to evaluate payload scalability. The experiments were performed using MATLAB R2022b on a system equipped with an Intel Core i5 2.9 GHz processor and 8 GB of RAM.

To evaluate the robustness of the proposed scheme, various intentional and unintentional attacks are applied to the watermarked images. Intentional attacks include JPEG compression with different quality factors, geometric distortions (rotation, resizing, cropping), and common filtering operations. In addition, the method is assessed against unintentional distortions such as speckle noise, salt-and-pepper noise, and Gaussian noise.

The perceptual quality and invisibility of the watermark are assessed using PSNR and SSIM, which measure the similarity between the original image $I$ and the watermarked image $I_W$. The PSNR and SSIM are defined as in Eqs. (36) and (37):

$$
\mathrm{PSNR}(I, I_W) = 10 \log_{10} \left( \frac{255^2}{\mathrm{MSE}(I, I_W)} \right)
$$

where the mean squared error (MSE) is:

$$
\mathrm{MSE}(I, I_W) = \frac{1}{mn} \sum_{i=1}^{m} \sum_{j=1}^{n} \left| I(i,j) - I_W(i,j) \right|^2
$$

$$
\mathrm{SSIM}(I, I_W) = \frac{\left(2\mu_I \mu_{I_W} + c_1\right) \left(2\,\mathrm{cov}(I, I_W) + c_2\right)}{\left(\mu_I^2 + \mu_{I_W}^2 + c_1\right) \left(\sigma_I^2 + \sigma_{I_W}^2 + c_2\right)}
$$

<p align="center"><b>Fig. 13.</b> Sample medical images used for testing. Adapted from [66]. (a) MRI-1 (529 × 498 pixels), (b) US-1 (538 × 460 pixels), (c) X-ray-1 (898 × 975 pixels).</p>

### 4.2. Performance analysis

Experimental results demonstrate that the proposed watermarking scheme is capable of successfully embedding data across various ROI sizes (4%, 8%, and 12%) and patient record sizes (2 kB, 6 kB, and 10 kB), as illustrated in Fig. 14. The extraction process successfully restored the original image (excluding the border area), under the condition that the watermarked image remained unaltered.

The reversible scheme effectively verifies the authenticity of an image by analyzing pixel-wise differences with the original version and by comparing hash values embedded in the ROI. Specifically, the hash value generated from the extracted ROI is compared with the originally embedded hash; a mismatch indicates tampering.

To demonstrate tamper detection and recovery capabilities, the method was tested on an ultrasound image with 12% ROI and 10 kB embedded payload. After intentionally modifying several pixels in the ROI, the proposed method successfully detected the tampering and restored the corrupted blocks using embedded recovery data, resulting in a quality improvement of +28.14 dB. The experimental results are depicted in Fig. 15.

### 4.3. Embedding capacity and visual quality evaluation

#### 4.3.1. Embedding performance

Table 1 presents a comprehensive comparison of embedding capacity and visual quality across 30 medical images with 10 kB of embedded data, including MRI, ultrasound (US), and X-ray modalities. The proposed method consistently achieves high-capacity reversible embedding across all three regions — ROI, RONI, and the border. For MRI images, the method achieves an average ROI capacity of 5.87 bpp, with the maximum value of 6 bpp occurring in MRI-1 and MRI-6 (8.27% and 2.88% ROI). The lowest ROI capacity is 5.30 bpp, observed in MRI-3 with a 3.78% ROI. For ultrasound images, the average ROI capacity is 5.74 bpp; the highest value of 6 bpp appears in US-2, US-9, and US-10 (5.43%, 6.61%, and 5.93% ROI), while the lowest capacity of 4.39 bpp is found in US-7 (4.19% ROI). X-ray images record the highest overall ROI performance with an average of 5.84 bpp, including multiple cases reaching 6 bpp (X-ray-1, -3, -4, -5, -6, -8, and -10, with ROI sizes of 2.86%, 4.99%, 6.76%, 7.99%, 8.42%, 5.53%, and 4.82%). The minimum capacity in this group is 4.47 bpp, observed in X-ray-7 (5.26% ROI). Nevertheless, this value remains substantially higher than those achieved by conventional reversible watermarking schemes.

In contrast, the RONI region exhibits greater variability because its effective capacity depends on ROI proportion and local texture. For the RONI region, the proposed method exhibits clear modality-dependent variations. MRI images achieve an average RONI capacity of 0.69 bpp, with values ranging from 0.34 bpp (MRI-3, 3.78% ROI) to 0.96 bpp (MRI-5, 4.73% ROI). Ultrasound images show a lower average of 0.52 bpp, with a minimum of 0.36 bpp (US-3, 6.01% ROI) and a maximum of 0.93 bpp (US-10, 5.93% ROI). X-ray images provide the highest RONI performance, with an average of 0.87 bpp, a minimum of 0.76 bpp (X-ray-10, 4.82% ROI), and a maximum of 0.98 bpp (X-ray-1, 2.86% ROI).

Overall, these results confirm that RONI capacity tends to increase as the ROI area becomes smaller, and X-ray images consistently achieve higher RONI capacities due to their more homogeneous and less textured background regions. In the RONI region, the proposed method employs a 2D Difference Expansion (2D-DE) scheme applied to LH1, HL1, and HH1 wavelet sub-bands. Unlike pixel-based DE, the 2D-DE technique enables data embedding in both smooth and non-smooth areas of the image, providing higher embedding flexibility and ensuring semi-fragile behavior suitable for tamper localization and recovery. Meanwhile, the border region produces a stable embedding capacity of exactly 1 bpp due to its fixed LSB-based embedding mechanism.

Overall, Table 1 demonstrates that the proposed approach can embed up to 10 kB of patient information within a 12% ROI while maintaining high image fidelity, with minimum PSNR values around 31 dB and SSIM values above 0.95, along with reasonable computational efficiency.

<p align="center"><b>Fig. 14.</b> Visual comparison of the original, watermarked, extracted, and difference images under varying ROI sizes and payload capacities for the US-1 image. (a) Original image (ROI 4.21%, 2 kB), (b) Watermarked image (PSNR 41.93 dB, SSIM 0.9851), (c) Extracted image (PSNR 70.29 dB, SSIM 0.9999), (d) Difference image after extraction, (e) Original image (ROI 8.17%, 6 kB), (f) Watermarked image (PSNR 39.83 dB, SSIM 0.9735), (g) Extracted image (PSNR 69.14 dB, SSIM 0.9999), (h) Difference image after extraction, (i) Original image (ROI 12.01%, 10 kB), (j) Watermarked image (PSNR 38.49 dB, SSIM 0.9641), (k) Extracted image (PSNR 67.92 dB, SSIM 0.9997), (l) Difference image after extraction.</p>

<p align="center"><b>Fig. 15.</b> Comparison between the original watermarked image, erase data from ROI, and the recovered result for the US-1 image. (a) Original image (ROI 12%, 10 kB), (b) Tampered image (PSNR 20.20 dB, SSIM 0.9817), (c) Hash value comparison, (d) Tampered area localization, (e) Pixel difference after extraction, (f) Recovered image (PSNR 48.30 dB, SSIM 0.9951).</p>

**Table 1.** Comparison of embedding capacity and visual quality across 30 medical images, consisting of 10 MRI, 10 ultrasound (US), and 10 X-ray images with 10 kB data.

| Images | Image size | ROI size (%) | Cap. ROI (bpp) | Cap. RONI (bpp) | Cap. Border (bpp) | Payload W1 (bpp) | Payload W2 (bpp) | Payload W3 (bpp) | PSNR W1 (dB) | PSNR W2 (dB) | PSNR W3 (dB) | SSIM W1 | SSIM W2 | SSIM W3 | Exec. time (s) | Exec. time/pixel (s×10⁻⁴) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MRI-1 | 529×498 | 8.27 | 6.00 | 0.78 | 1.00 | 1.23 | 0.23 | 0.25 | 52.89 | 41.00 | 40.99 | 0.9980 | 0.9885 | 0.9884 | 48.11 | 1.83 |
| MRI-2 | 436×436 | 8.39 | 5.87 | 0.53 | 1.00 | 1.68 | 0.34 | 0.57 | 48.11 | 37.37 | 37.36 | 0.9968 | 0.9756 | 0.9753 | 41.84 | 2.20 |
| MRI-3 | 712×712 | 3.78 | 5.30 | 0.34 | 1.00 | 1.39 | 0.12 | 0.40 | 48.56 | 38.04 | 38.03 | 0.9987 | 0.9904 | 0.9902 | 53.71 | 1.06 |
| MRI-4 | 517×446 | 4.39 | 5.97 | 0.83 | 1.00 | 2.64 | 0.23 | 0.30 | 44.32 | 39.85 | 39.84 | 0.9970 | 0.9853 | 0.9852 | 37.21 | 1.61 |
| MRI-5 | 634×610 | 4.73 | 5.99 | 0.96 | 1.00 | 1.46 | 0.16 | 0.15 | 50.09 | 44.82 | 44.81 | 0.9981 | 0.9949 | 0.9949 | 43.96 | 1.14 |
| MRI-6 | 726×732 | 2.88 | 6.00 | 0.92 | 1.00 | 1.74 | 0.11 | 0.12 | 52.13 | 50.53 | 50.52 | 0.9989 | 0.9974 | 0.9974 | 44.99 | 0.85 |
| MRI-7 | 460×460 | 5.20 | 5.74 | 0.44 | 1.00 | 2.43 | 0.27 | 0.54 | 42.49 | 33.46 | 33.46 | 0.9964 | 0.9698 | 0.9697 | 39.35 | 1.86 |
| MRI-8 | 418×362 | 5.89 | 5.99 | 0.43 | 1.00 | 3.00 | 0.38 | 0.54 | 45.57 | 33.31 | 33.31 | 0.9957 | 0.9641 | 0.9638 | 27.33 | 1.81 |
| MRI-9 | 436×437 | 6.37 | 5.99 | 0.83 | 1.00 | 2.20 | 0.31 | 0.36 | 47.15 | 36.13 | 36.13 | 0.9963 | 0.9683 | 0.9682 | 35.77 | 1.88 |
| MRI-10 | 424×460 | 6.76 | 5.90 | 0.83 | 1.00 | 2.03 | 0.31 | 0.33 | 45.90 | 37.69 | 37.69 | 0.9962 | 0.9806 | 0.9805 | 36.88 | 1.89 |
| **Average MRI** | — | 5.67 | 5.87 | 0.69 | 1.00 | 1.98 | 0.25 | 0.36 | 47.72 | 39.22 | 39.21 | 0.9972 | 0.9815 | 0.9814 | 40.92 | 1.61 |
| US-1 | 538×460 | 4.76 | 5.98 | 0.48 | 1.00 | 2.27 | 0.24 | 0.34 | 48.51 | 38.85 | 38.85 | 0.9977 | 0.9672 | 0.9670 | 33.00 | 1.33 |
| US-2 | 600×450 | 5.43 | 6.00 | 0.39 | 1.00 | 1.82 | 0.20 | 0.34 | 49.17 | 35.44 | 35.44 | 0.9979 | 0.9697 | 0.9696 | 41.19 | 1.53 |
| US-3 | 640×480 | 6.01 | 5.95 | 0.36 | 1.00 | 1.45 | 0.21 | 0.35 | 50.81 | 39.77 | 39.76 | 0.9986 | 0.9834 | 0.9834 | 45.11 | 1.47 |
| US-4 | 640×480 | 4.66 | 5.97 | 0.37 | 1.00 | 1.86 | 0.19 | 0.32 | 49.06 | 39.52 | 39.51 | 0.9985 | 0.9834 | 0.9833 | 37.98 | 1.24 |
| US-5 | 271×321 | 5.84 | 5.99 | 0.70 | 1.00 | 5.26 | 0.62 | 0.35 | 43.84 | 32.15 | 32.15 | 0.9918 | 0.8867 | 0.8866 | 19.67 | 2.26 |
| US-6 | 592×403 | 4.61 | 5.95 | 0.45 | 1.00 | 2.43 | 0.25 | 0.35 | 46.79 | 35.98 | 35.97 | 0.9981 | 0.9744 | 0.9743 | 35.11 | 1.47 |
| US-7 | 1126×938 | 4.19 | 4.39 | 0.50 | 1.00 | 0.60 | 0.08 | 0.17 | 60.99 | 46.78 | 46.77 | 0.9997 | 0.9951 | 0.9950 | 95.87 | 0.91 |
| US-8 | 560×410 | 5.93 | 5.17 | 0.40 | 1.00 | 1.96 | 0.26 | 0.50 | 44.92 | 31.57 | 31.57 | 0.9975 | 0.9579 | 0.9575 | 34.87 | 1.52 |
| US-9 | 745×553 | 6.61 | 6.00 | 0.62 | 1.00 | 0.98 | 0.17 | 0.20 | 56.98 | 43.07 | 43.06 | 0.9990 | 0.9880 | 0.9880 | 54.74 | 1.33 |
| US-10 | 750×489 | 5.93 | 6.00 | 0.93 | 1.00 | 1.23 | 0.18 | 0.13 | 56.35 | 40.66 | 40.66 | 0.9991 | 0.9877 | 0.9877 | 58.77 | 1.60 |
| **Average US** | — | 5.40 | 5.74 | 0.52 | 1.00 | 1.99 | 0.24 | 0.31 | 50.74 | 38.38 | 38.37 | 0.9978 | 0.9694 | 0.9692 | 45.63 | 1.47 |
| X-ray-1 | 898×975 | 2.86 | 6.00 | 0.98 | 1.00 | 1.07 | 0.07 | 0.12 | 56.87 | 50.27 | 50.26 | 0.9991 | 0.9959 | 0.9959 | 65.06 | 0.74 |
| X-ray-2 | 576×579 | 5.09 | 5.96 | 0.82 | 1.00 | 1.57 | 0.19 | 0.19 | 53.93 | 40.74 | 40.74 | 0.9982 | 0.9742 | 0.9742 | 42.93 | 1.29 |
| X-ray-3 | 451×513 | 4.99 | 6.00 | 0.93 | 1.00 | 2.32 | 0.25 | 0.17 | 52.56 | 40.66 | 40.66 | 0.9974 | 0.9724 | 0.9724 | 33.48 | 1.45 |
| X-ray-4 | 509×514 | 6.76 | 6.00 | 0.78 | 1.00 | 1.51 | 0.24 | 0.21 | 52.86 | 39.72 | 39.72 | 0.9977 | 0.9672 | 0.9672 | 41.33 | 1.58 |
| X-ray-5 | 437×516 | 7.99 | 6.00 | 0.84 | 1.00 | 1.48 | 0.28 | 0.17 | 51.96 | 38.70 | 38.70 | 0.9975 | 0.9643 | 0.9643 | 40.15 | 1.78 |
| X-ray-6 | 368×490 | 8.42 | 6.00 | 0.88 | 1.00 | 1.76 | 0.35 | 0.17 | 47.78 | 39.90 | 39.90 | 0.9963 | 0.9530 | 0.9530 | 35.33 | 1.96 |
| X-ray-7 | 898×975 | 3.54 | 5.99 | 0.97 | 1.00 | 0.86 | 0.08 | 0.12 | 57.32 | 50.10 | 50.09 | 0.9992 | 0.9958 | 0.9958 | 81.56 | 0.93 |
| X-ray-8 | 1908×1808 | 5.53 | 6.00 | 0.93 | 1.00 | 0.14 | 0.04 | 0.04 | 68.22 | 55.55 | 55.54 | 0.9999 | 0.9983 | 0.9983 | 350.74 | 1.02 |
| X-ray-9 | 843×808 | 5.26 | 4.47 | 0.84 | 1.00 | 0.75 | 0.11 | 0.13 | 56.94 | 43.71 | 43.71 | 0.9991 | 0.9852 | 0.9852 | 72.18 | 1.06 |
| X-ray-10 | 1084×1232 | 4.82 | 6.00 | 0.76 | 1.00 | 0.41 | 0.07 | 0.12 | 63.96 | 49.59 | 49.58 | 0.9997 | 0.9950 | 0.9950 | 128.45 | 0.96 |
| **Average X-ray** | — | 5.53 | 5.84 | 0.87 | 1.00 | 1.19 | 0.17 | 0.14 | 56.24 | 44.90 | 44.89 | 0.9984 | 0.9801 | 0.9801 | 89.12 | 1.28 |

#### 4.3.2. Visual quality after embedding

The visual fidelity of the watermarked images remains high across all modalities and ROI configurations, as summarized in Table 1. MRI images generally achieve the highest embedding quality, with PSNR values consistently above 40 dB across most ROI and payload settings. Ultrasound images exhibit slightly lower PSNR and SSIM due to their speckle-rich texture, but the perceptual quality remains acceptable. X-ray images achieve the highest overall fidelity, benefiting from smoother structural characteristics that yield superior PSNR and SSIM values.

Table 2 further illustrates pixel-level quality changes in MRI-1, US-1, and X-ray-1. As ROI size increases from approximately 4% to 12% and payload grows from 2 kB to 10 kB, a gradual reduction in PSNR is observed across modalities. However, even under the largest ROI and payload conditions, the proposed scheme maintains PSNR above 35 dB and SSIM above 0.95, demonstrating that the adaptive bit-level expansion and pixel shifting strategy effectively preserves perceptual fidelity.

**Table 2.** Comparison of embedding capacity, payload distribution, and visual quality for the MRI-1, US-1, and X-ray-1 images under different data sizes and ROI configurations.

| Images | Data size | ROI size (%) | Cap. ROI (bpp) | Cap. RONI (bpp) | Cap. Border (bpp) | Payload W1 (bpp) | Payload W2 (bpp) | Payload W3 (bpp) | PSNR W1 (dB) | PSNR W2 (dB) | PSNR W3 (dB) | SSIM W1 | SSIM W2 | SSIM W3 | Exec. time (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MRI-1 | 2 kB | 3.92 | 6.00 | 0.79 | 1.00 | 0.93 | 0.11 | 0.20 | 57.24 | 45.36 | 45.35 | 0.9956 | 0.9994 | 0.9957 | 37.97 |
| MRI-1 | 2 kB | 8.09 | 6.00 | 0.78 | 1.00 | 0.45 | 0.14 | 0.21 | 59.63 | 43.39 | 43.39 | 0.9995 | 0.9945 | 0.9944 | 46.14 |
| MRI-1 | 2 kB | 11.87 | 5.99 | 0.77 | 1.00 | 0.31 | 0.16 | 0.24 | 57.32 | 42.75 | 42.74 | 0.9994 | 0.9936 | 0.9935 | 60.16 |
| MRI-1 | 6 kB | 4.07 | 6.00 | 0.80 | 1.00 | 1.74 | 0.16 | 0.25 | 52.81 | 42.07 | 42.06 | 0.9984 | 0.9919 | 0.9918 | 31.86 |
| MRI-1 | 6 kB | 8.06 | 6.00 | 0.78 | 1.00 | 0.88 | 0.19 | 0.25 | 56.26 | 41.71 | 41.70 | 0.9990 | 0.9913 | 0.9911 | 47.99 |
| MRI-1 | 6 kB | 12.50 | 6.00 | 0.77 | 1.00 | 0.57 | 0.24 | 0.25 | 56.84 | 41.27 | 41.27 | 0.9991 | 0.9900 | 0.9898 | 61.44 |
| MRI-1 | 10 kB | 4.14 | 6.00 | 0.80 | 1.00 | 2.45 | 0.21 | 0.25 | 51.16 | 41.02 | 41.02 | 0.9976 | 0.9885 | 0.9884 | 33.18 |
| MRI-1 | 10 kB | 8.10 | 6.00 | 0.78 | 1.00 | 1.25 | 0.23 | 0.25 | 52.78 | 40.95 | 40.94 | 0.9979 | 0.9884 | 0.9883 | 47.10 |
| MRI-1 | 10 kB | 12.06 | 6.00 | 0.77 | 1.00 | 0.84 | 0.29 | 0.26 | 54.76 | 40.28 | 40.27 | 0.9985 | 0.9866 | 0.9865 | 63.90 |
| US-1 | 2 kB | 4.21 | 5.98 | 0.49 | 1.00 | 0.92 | 0.11 | 0.23 | 53.35 | 41.94 | 41.93 | 0.9993 | 0.9851 | 0.9851 | 33.16 |
| US-1 | 2 kB | 7.90 | 5.99 | 0.46 | 1.00 | 0.49 | 0.14 | 0.25 | 54.03 | 41.43 | 41.43 | 0.9995 | 0.9824 | 0.9824 | 43.97 |
| US-1 | 2 kB | 12.03 | 5.99 | 0.44 | 1.00 | 0.32 | 0.18 | 0.26 | 54.19 | 40.80 | 40.79 | 0.9994 | 0.9791 | 0.9791 | 54.13 |
| US-1 | 6 kB | 4.29 | 5.97 | 0.48 | 1.00 | 1.76 | 0.18 | 0.30 | 49.90 | 40.04 | 40.04 | 0.9984 | 0.9757 | 0.9756 | 32.26 |
| US-1 | 6 kB | 8.17 | 5.99 | 0.46 | 1.00 | 0.92 | 0.21 | 0.30 | 51.40 | 39.84 | 39.83 | 0.9989 | 0.9736 | 0.9735 | 44.14 |
| US-1 | 6 kB | 12.31 | 5.99 | 0.43 | 1.00 | 0.61 | 0.25 | 0.34 | 53.10 | 39.35 | 39.35 | 0.9991 | 0.9704 | 0.9703 | 58.31 |
| US-1 | 10 kB | 4.26 | 5.98 | 0.48 | 1.00 | 2.53 | 0.23 | 0.33 | 47.92 | 38.76 | 38.76 | 0.9975 | 0.9675 | 0.9673 | 33.24 |
| US-1 | 10 kB | 8.02 | 5.99 | 0.46 | 1.00 | 1.35 | 0.26 | 0.34 | 49.41 | 38.70 | 38.70 | 0.9980 | 0.9658 | 0.9657 | 44.60 |
| US-1 | 10 kB | 12.01 | 5.99 | 0.43 | 1.00 | 0.90 | 0.29 | 0.37 | 50.31 | 38.49 | 38.49 | 0.9985 | 0.9643 | 0.9641 | 57.25 |
| X-ray-1 | 2 kB | 4.01 | 6.00 | 0.98 | 1.00 | 0.27 | 0.05 | 0.12 | 64.92 | 53.94 | 53.91 | 0.9998 | 0.9979 | 0.9979 | 80.92 |
| X-ray-1 | 2 kB | 8.24 | 6.00 | 0.97 | 1.00 | 0.13 | 0.07 | 0.12 | 66.26 | 51.67 | 51.65 | 0.9999 | 0.9968 | 0.9968 | 148.76 |
| X-ray-1 | 2 kB | 12.24 | 6.00 | 0.97 | 1.00 | 0.09 | 0.10 | 0.13 | 66.44 | 50.08 | 50.06 | 0.9999 | 0.9958 | 0.9958 | 166.75 |
| X-ray-1 | 6 kB | 4.20 | 6.00 | 0.97 | 1.00 | 0.51 | 0.07 | 0.12 | 63.12 | 51.94 | 51.92 | 0.9997 | 0.9969 | 0.9969 | 77.64 |
| X-ray-1 | 6 kB | 8.04 | 6.00 | 0.97 | 1.00 | 0.27 | 0.09 | 0.12 | 62.99 | 50.14 | 50.13 | 0.9997 | 0.9958 | 0.9958 | 124.52 |
| X-ray-1 | 6 kB | 11.91 | 6.00 | 0.97 | 1.00 | 0.18 | 0.11 | 0.12 | 63.35 | 48.96 | 48.95 | 0.9997 | 0.9948 | 0.9948 | 184.52 |
| X-ray-1 | 10 kB | 4.15 | 6.00 | 0.98 | 1.00 | 0.73 | 0.08 | 0.12 | 61.20 | 50.47 | 50.46 | 0.9995 | 0.9959 | 0.9959 | 83.84 |
| X-ray-1 | 10 kB | 8.31 | 6.00 | 0.97 | 1.00 | 0.37 | 0.11 | 0.12 | 61.40 | 48.80 | 48.79 | 0.9996 | 0.9946 | 0.9946 | 130.55 |
| X-ray-1 | 10 kB | 12.40 | 6.00 | 0.97 | 1.00 | 0.25 | 0.14 | 0.12 | 61.81 | 47.84 | 47.83 | 0.9996 | 0.9934 | 0.9934 | 180.73 |

#### 4.3.3. Visual quality after extraction

The reversibility of the proposed method is validated through post-extraction image quality analysis. While the ROI and RONI regions employ fully reversible mechanisms, the border region uses a nonreversible 1-bit LSB embedding, which introduces a small, predictable loss. Nevertheless, Tables 1 and 2 show that this degradation is minimal.

Across MRI, ultrasound, and X-ray datasets, post-extraction PSNR consistently exceeds 65 dB, and SSIM approaches 1.0, indicating that almost all embedding-induced distortions are perfectly removed except for the single-bit modification in the border. X-ray images again display the highest post-extraction quality, owing to their smoother low-frequency characteristics.

The payload distribution across regions ($W_1$, $W_2$, and $W_3$) also confirms efficient resource utilization. As payload increases from 2 kB to 10 kB, $W_1$ (ROI) increases proportionally, while $W_2$ (RONI) and $W_3$ (border) remain within their predictable capacity limits. Despite these variations, visual quality remains consistently high, with average PSNR values of 39.21 dB and SSIM 0.9814 for MRI images, 38.37 dB and SSIM 0.9692 for ultrasound images, and 44.89 dB and SSIM 0.9801 for X-ray images. These findings confirm that the proposed scheme accommodates diverse payload sizes and ROI configurations without compromising reversibility, perceptual quality, or embedding efficiency.

### 4.4. Robustness, tamper detection, localization, and recovery

To evaluate the effectiveness of the proposed reversible watermarking scheme under both intentional and unintentional perturbations, we conducted a comprehensive set of attacks on the watermarked US-1 image. Attacks A-S (Figs. 16-20) include common image processing operations and noise models such as blur, salt-and-pepper (SP) noise at several densities, Poisson noise, Gaussian noise (AGN), median filtering, motion blur, sharpening, smoothing, cropping, resizing, JPEG compression (70%), Wiener filtering, Sobel operator, histogram equalization, geometric rotation, copy-and-paste, and others. After each attack we extracted the watermark and evaluated (1) the ROI reconstruction quality using PSNR and SSIM and (2) the global effect on the whole image by comparing the recovered image with the original cover image.

For clarity, the metrics reported in Table 3 follow these definitions:

- **Improve (ROI)** = PSNR/SSIM(Recovery) − PSNR/SSIM(Tampered), which quantifies the gain in ROI quality obtained by the recovery procedure;
- **Difference (Whole image)** = PSNR/SSIM(Original) − PSNR/SSIM(Recovery), which indicates how much the recovered image still differs from the original cover image.

Key observations from the experiments are:

**ROI recovery is highly effective for severe localized tampering.** Attacks that directly alter or erase ROI content show very large ROI improvements after recovery. For example, "Erase data from ROI" yields ROI PSNR of 19.92 dB (tampered) and 48.06 dB (recovered), i.e., an improvement of 28.14 dB, and SSIM increases from 0.9807 to 0.9949 (Improve = 0.0143). Similarly, "Adding new substance" produces ROI improvement of 27.07 dB. These results demonstrate the scheme's strong ability to restore high-fidelity ROI content after gross tampering.

**Recovery yields high structural fidelity in ROI across many attacks.** For most attacks the recovered ROI SSIM is very close to 1.0 (commonly $\geq$ 0.97), indicating that the recovered ROI preserves structure and perceptual quality. Examples: Sobel (recovered SSIM = 0.9953), Cropping (recovered SSIM = 0.9911), and many SP settings (recovered SSIM $\approx$ 0.998-0.999).

**Global (whole-image) difference is expected and consistent with definitions.** The Difference (Whole image) values are generally negative (Original − Recovery < 0) because the recovered image is compared to the original cover image: a negative value simply indicates that the recovered image's PSNR or SSIM is slightly lower than the original cover (after recovery). This behavior is consistent across attacks and reflects the fact that recovery focuses on restoring the ROI with minimal guarantee on globally identical pixels.

**Attacks with minor ROI damage show modest improvements (smaller numerical gains).** Some image-wide operations or mild noise produce relatively small ROI Improve values. For example, JPEG compression (70%) yields Improve (ROI) = 0.22 dB (PSNR tampered 41.75 → recovered 41.97 dB), and Gaussian filter/Poisson/AGN produce improvements in the range 1-1.6 dB. These small improvements indicate that when the ROI itself is not heavily corrupted, recovery still works but the numerical gain is limited.

**Method limitations — specific attacks that reduce or do not improve ROI quality.** A few operations are problematic or marginal for our scheme: notably the Wiener attack shows a slight decrease in ROI PSNR after recovery (Tampered 42.63 dB → Recovery 42.41 dB, Improve = −0.22 dB), indicating imperfect recovery under this filter. Resize and certain filtering operations also produce relatively small improvements (e.g., Resize Improve $\approx$ 7.36 dB, Sobel Improve $\approx$ 14.80 dB), meaning recovery is less effective compared with direct ROI erasure/insertion cases. These findings indicate that geometric/resampling operations and some linear filters can reduce recovery performance and should be considered as challenging cases.

**Overall robustness conclusion.** Taken together, the results in Table 3 show that the proposed technique is robust for ROI tamper detection and recovery across a wide spectrum of attacks: it can restore ROI content to high PSNR (>40 dB in many cases) and very high SSIM (>0.97) for the majority of attacks, especially for localized tampering (erase/insert). The method is less effective for certain whole-image filters and resampling (Wiener, aggressive resizes, strong low-pass filtering), where recovery gains are small or negative. These limitations suggest directions for future work (e.g., improved handling of resampling and linear filtering during recovery).

**Practical implication.** Because medical decisions often rely on ROI integrity, the high ROI recovery PSNR/SSIM observed for the most critical attack types (erase/insert, copy-paste, cropping) indicates that the proposed scheme is suitable for protecting sensitive medical regions against tampering while maintaining diagnostic-level visual fidelity.

Table 3 presents the quantitative evaluation of the recovered ROI after 22 tampering and signal-processing attacks. The proposed scheme consistently maintains high reconstruction fidelity, with PSNR values exceeding 40 dB for all test cases and reaching up to 48.50 dB. The SSIM values range from 0.9726 to 0.9954, indicating that the structural details of the ROI are preserved extremely well despite the use of lossy JPEG2000 compression for embedding the recovery data.

Figs. 16-20 provide visual examples of the recovered ROI for representative attack categories. The reconstructed regions show no noticeable artifacts or diagnostic distortion, further confirming that the JPEG2000 compression level used in this work does not degrade the clinical interpretability of the ROI. These results support the appropriateness of using lossy JPEG2000, as it offers substantial size reduction needed for RONI embedding while maintaining high recovery fidelity.

Finally, note that the numeric examples given above are directly taken from Table 3 (PSNR and SSIM columns). For reproducibility, we include the exact per-attack figures in the table and reference the illustrative attack images in Figs. 16-20. Because the ROI recovery uses lossy compression data, patient information $D$ embedded reversibly in the ROI can only be extracted reliably when no tampering occurs. When the ROI has been modified and subsequently reconstructed from lossy data, $D$ becomes partially or fully unrecoverable and is therefore marked as invalid in the extraction results.

**Table 3.** Analysis of PSNR and SSIM values for ROI tampering and recovery on the US-1 image after various attacks (A–V), corresponding to Figs. 16-20.

*High improvement*

| Attack type | PSNR ROI Tampered (dB) | PSNR ROI Recovery (dB) | PSNR ROI Improve^a (dB) | PSNR Whole Tampered (dB) | PSNR Whole Recovery (dB) | PSNR Whole Difference^b (dB) | SSIM ROI Tampered | SSIM ROI Recovery | SSIM ROI Improve^a | SSIM Whole Tampered | SSIM Whole Recovery | SSIM Whole Difference^b |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A. Erase data from ROI | 19.92 | 48.06 | 28.14 | 20.20 | 48.30 | -19.62 | 0.9807 | 0.9949 | 0.0143 | 0.9817 | 0.9951 | -0.0047 |
| B. Adding new substance | 21.22 | 48.29 | 27.07 | 21.51 | 48.53 | -19.39 | 0.9776 | 0.9953 | 0.0177 | 0.9788 | 0.9954 | -0.0044 |
| C. Histogram equalization | 18.99 | 41.26 | 22.28 | 19.27 | 41.54 | -26.38 | 0.9204 | 0.9774 | 0.0570 | 0.9253 | 0.9786 | -0.0212 |
| D. Adjust | 22.60 | 42.00 | 19.40 | 22.88 | 42.27 | -25.65 | 0.9372 | 0.9782 | 0.0410 | 0.9411 | 0.9794 | -0.0204 |
| E. Cropping (64×64) | 27.98 | 46.47 | 18.49 | 28.27 | 46.72 | -21.20 | 0.9609 | 0.9911 | 0.0302 | 0.9632 | 0.9915 | -0.0083 |
| F. Sobel | 31.53 | 46.33 | 14.80 | 31.82 | 46.59 | -21.33 | 0.9859 | 0.9953 | 0.0094 | 0.9866 | 0.9954 | -0.0044 |
| G. Geometric rotation | 27.72 | 42.04 | 14.32 | 28.00 | 42.31 | -25.61 | 0.9164 | 0.9779 | 0.0615 | 0.9216 | 0.9791 | -0.0207 |
| H. Salt and Pepper (0.01) | 34.70 | 45.09 | 10.40 | 34.98 | 45.36 | -22.57 | 0.9749 | 0.9898 | 0.0149 | 0.9763 | 0.9903 | -0.0095 |

*Middle improvement*

| Attack type | PSNR ROI Tampered (dB) | PSNR ROI Recovery (dB) | PSNR ROI Improve^a (dB) | PSNR Whole Tampered (dB) | PSNR Whole Recovery (dB) | PSNR Whole Difference^b (dB) | SSIM ROI Tampered | SSIM ROI Recovery | SSIM ROI Improve^a | SSIM Whole Tampered | SSIM Whole Recovery | SSIM Whole Difference^b |
|---|---|---|---|---|---|---|---|---|---|---|---|
| I. Copy and paste | 38.55 | 47.94 | 9.39 | 38.83 | 48.18 | -19.74 | 0.9871 | 0.9947 | 0.0076 | 0.9877 | 0.9948 | -0.0050 |
| J. Resize | 33.11 | 40.47 | 7.36 | 33.40 | 40.75 | -27.17 | 0.9314 | 0.9739 | 0.0425 | 0.9356 | 0.9753 | -0.0244 |
| K. Median filter (4×4) | 37.61 | 42.33 | 4.72 | 37.89 | 42.60 | -25.32 | 0.9688 | 0.9793 | 0.0104 | 0.9707 | 0.9804 | -0.0194 |
| L. Motion blur | 37.23 | 41.55 | 4.32 | 37.51 | 41.83 | -26.10 | 0.9573 | 0.9766 | 0.0193 | 0.9599 | 0.9779 | -0.0219 |
| M. Speckle attack | 35.84 | 39.92 | 4.07 | 36.12 | 40.19 | -27.73 | 0.9520 | 0.9709 | 0.0189 | 0.9549 | 0.9726 | -0.0272 |
| N. Blur | 38.33 | 41.48 | 3.14 | 38.61 | 41.75 | -26.17 | 0.9662 | 0.9768 | 0.0106 | 0.9682 | 0.9781 | -0.0217 |
| O. Average filtering (4×4) | 39.10 | 42.16 | 3.06 | 39.38 | 42.43 | -25.49 | 0.9738 | 0.9790 | 0.0051 | 0.9753 | 0.9801 | -0.0197 |

*Low improvement*

| Attack type | PSNR ROI Tampered (dB) | PSNR ROI Recovery (dB) | PSNR ROI Improve^a (dB) | PSNR Whole Tampered (dB) | PSNR Whole Recovery (dB) | PSNR Whole Difference^b (dB) | SSIM ROI Tampered | SSIM ROI Recovery | SSIM ROI Improve^a | SSIM Whole Tampered | SSIM Whole Recovery | SSIM Whole Difference^b |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P. Gaussian filter | 41.29 | 42.83 | 1.55 | 41.56 | 43.10 | -24.82 | 0.9851 | 0.9841 | -0.0011 | 0.9859 | 0.9849 | -0.0149 |
| Q. Poisson attack | 39.98 | 41.34 | 1.37 | 40.26 | 41.62 | -26.30 | 0.9728 | 0.9760 | 0.0032 | 0.9744 | 0.9773 | -0.0225 |
| R. AGN (0.0008) | 40.65 | 41.71 | 1.06 | 40.92 | 41.99 | -25.94 | 0.9751 | 0.9775 | 0.0024 | 0.9765 | 0.9787 | -0.0211 |
| S. Sharpening | 42.54 | 43.29 | 0.75 | 42.81 | 43.56 | -24.36 | 0.9932 | 0.9895 | -0.0037 | 0.9934 | 0.9899 | -0.0098 |
| T. Smoothing | 43.30 | 44.03 | 0.72 | 43.57 | 44.29 | -23.63 | 0.9913 | 0.9885 | -0.0028 | 0.9917 | 0.9890 | -0.0108 |
| U. JPEG compression 70% | 41.75 | 41.97 | 0.22 | 42.02 | 42.24 | -25.68 | 0.9798 | 0.9786 | -0.0012 | 0.9809 | 0.9798 | -0.0200 |
| V. Wiener attack | 42.63 | 42.41 | -0.22 | 42.90 | 42.68 | -25.24 | 0.9760 | 0.9772 | 0.0012 | 0.9774 | 0.9785 | -0.0213 |

^a Improve (ROI) = Recovery − Tampered.

^b Difference (Whole Image): PSNR/SSIM (original image) − PSNR/SSIM (recovered image).

<p align="center"><b>Fig. 16.</b> Demonstration of ROI tampering and recovery on the US-1 image. (a) Watermarked image (no attack), (b) Selected ROI, (c) Extracted ROI, (d) Extracted image, (e) Tamper A: Erase data from ROI, (f) ROI after Tamper A, (g) Recovered ROI (A), (h) Recovered image (A), (i) Tamper B: Adding new substance, (j) ROI after Tamper B, (k) Recovered ROI (B), (l) Recovered image (B), (m) Tamper C: Histogram equalization, (n) ROI after Tamper C, (o) Recovered ROI (C), (p) Recovered image (C), (q) Tamper D: Adjust, (r) ROI after Tamper D, (s) Recovered ROI (D), (t) Recovered image (D).</p>

<p align="center"><b>Fig. 17.</b> Demonstration of ROI tampering and recovery on the US-1 image. (a) Tamper E: Cropping (64×64), (b) ROI after Tamper E, (c) Recovered ROI (E), (d) Recovered image (E), (e) Tamper F: Sobel, (f) ROI after Tamper F, (g) Recovered ROI (F), (h) Recovered image (F), (i) Tamper G: Geometric rotation, (j) ROI after Tamper G, (k) Recovered ROI (G), (l) Recovered image (G), (m) Tamper H: Salt and Pepper (0.01), (n) ROI after Tamper H, (o) Recovered ROI (H), (p) Recovered image (H), (q) Tamper I: Copy and paste, (r) ROI after Tamper I, (s) Recovered ROI (I), (t) Recovered image (I).</p>

<p align="center"><b>Fig. 18.</b> Demonstration of ROI tampering and recovery on the US-1 image. (a) Tamper J: Resize, (b) ROI after Tamper J, (c) Recovered ROI (J), (d) Recovered image (J), (e) Tamper K: Median filter (4×4), (f) ROI after Tamper K, (g) Recovered ROI (K), (h) Recovered image (K), (i) Tamper L: Motion blur, (j) ROI after Tamper L, (k) Recovered ROI (L), (l) Recovered image (L), (m) Tamper M: Speckle attack, (n) ROI after Tamper M, (o) Recovered ROI (M), (p) Recovered image (M), (q) Tamper N: Blur, (r) ROI after Tamper N, (s) Recovered ROI (N), (t) Recovered image (N).</p>

<p align="center"><b>Fig. 19.</b> Demonstration of ROI tampering and recovery on the US-1 image. (a) Tamper O: Average filtering (4×4), (b) ROI after Tamper O, (c) Recovered ROI (O), (d) Recovered image (O), (e) Tamper P: Gaussian filter, (f) ROI after Tamper P, (g) Recovered ROI (P), (h) Recovered image (P), (i) Tamper Q: Poisson attack, (j) ROI after Tamper Q, (k) Recovered ROI (Q), (l) Recovered image (Q), (m) Tamper R: AGN (0.0008), (n) ROI after Tamper R, (o) Recovered ROI (R), (p) Recovered image (R), (q) Tamper S: Sharpening, (r) ROI after Tamper S, (s) Recovered ROI (S), (t) Recovered image (S).</p>

<p align="center"><b>Fig. 20.</b> Demonstration of ROI tampering and recovery on the US-1 image. (a) Tamper T: Smoothing, (b) ROI after Tamper T, (c) Recovered ROI (T), (d) Recovered image (T), (e) Tamper U: JPEG compression 70%, (f) ROI after Tamper U, (g) Recovered ROI (U), (h) Recovered image (U), (i) Tamper V: Wiener attack, (j) ROI after Tamper V, (k) Recovered ROI (V), (l) Recovered image (V).</p>

### 4.5. Comparison with state-of-the-art

Tables 4 and 5 present a comprehensive comparative evaluation between the proposed scheme and representative state-of-the-art medical image watermarking methods reported in the literature. The comparison is conducted in terms of imperceptibility, robustness, reversibility, embedding capacity, and functional capabilities including tamper detection, localization, and recovery. Reported experimental results from the original publications are adopted to ensure a fair and consistent comparison under comparable evaluation settings.

In terms of imperceptibility, most existing reversible watermarking schemes report high PSNR values only under relatively low embedding capacities, typically below 2 bpp, as summarized in Table 5. Although several methods achieve PSNR values exceeding 50 dB, such performance is often obtained at the expense of limited payload or lack of reversibility. In contrast, the proposed scheme maintains acceptable visual quality (PSNR above 35 dB) while supporting significantly higher embedding capacity (up to 6 bpp) in the ROI, which is essential for embedding complete electronic patient records (EPR) without perceptible degradation.

Regarding robustness, as shown in Table 4, the majority of ROI-based reversible watermarking schemes are inherently fragile and fail to withstand common signal processing operations. Fully robust watermarking approaches reported in the literature typically sacrifice reversibility and precise tamper localization. By employing a semi-fragile embedding strategy in the RONI region, the proposed scheme achieves improved robustness against common unintentional manipulations while preserving reversibility and accurate tamper localization. This balanced trade-off between imperceptibility, robustness, and reversibility is not simultaneously achieved by most existing state-of-the-art methods.

Despite its advantages, the proposed scheme has several limitations. First, full reversibility is guaranteed only within the ROI and RONI regions, while the border region is designed for robustness rather than reversibility. Second, the embedding process involves multi-layer operations, which may increase computational complexity compared to simple LSB-based approaches. However, these limitations do not reduce the applicability of the proposed method in clinical scenarios, as the design prioritizes diagnostic integrity, security, and reliable tamper recovery, which are critical requirements in medical image management systems.

**Table 4.** General comparison between some medical image watermarking schemes.

| Scheme | ROI based | Tamper detection | Tamper localization | Tamper recovery | Reversibility | Robustness |
|---|---|---|---|---|---|---|
| Al-Qershi and Khoo [56] | √ | Only-ROI | Only-ROI | Only-ROI | ROI & RONI | × |
| Al-Qershi and Khoo [57] | √ | Only-ROI | Only-ROI | Only-ROI | ROI & RONI | × |
| Al-Qershi and Khoo [52] | √ | Only-ROI | Only-ROI | Only-ROI | ROI | √ |
| Gao et al. [67] | √ | Only-ROI | Only-ROI | × | ROI | × |
| Khor et al. [68] | √ | Only-ROI | Only-ROI | Only-ROI | × | × |
| Chaitanya and Gangadhara Rao [69] | √ | Only-ROI | Only-ROI | Only-ROI | × | × |
| Chaitanya and Gangadhara Rao [70] | √ | Only-ROI | Only-ROI | Only-ROI | × | × |
| Barani et al. [29] | × | √ | √ | × | × | √ |
| Abdelhakim et al. [32] | × | √ | √ | √ | × | √ |
| Swaraja et al. [71] | √ | √ | √ | × | × | √ |
| Sivasubramanian and Konganathan [28] | × | √ | √ | √ | × | √ |
| Molina-García et al. [31] | × | √ | √ | √ | × | × |
| Sarkar et al. [30] | × | √ | √ | √ | × | √ |
| Golea et al. [72] | √ | Only-ROI | Only-ROI | Only-ROI | × | √ |
| Ravichandran et al. [73] | √ | Only-ROI | Only-ROI | Only-ROI | × | √ |
| Alshanbari [74] | √ | Only-ROI | × | Only-ROI | × | √ |
| Shi et al. [75] | √ | Only-ROI | Only-ROI | Only-ROI | √ | √ |
| Laishram and Manglem Singh [76] | √ | Only-ROI | × | × | × | √ |
| Nazari and Mehrabian [10] | √ | √ | √ | × | × | √ |
| Hussan et al. [27] | × | √ | √ | √ | × | √ |
| Hussan et al. [77] | × | √ | √ | √ | × | √ |
| Soualmi et al. [78] | √ | √ | × | × | × | √ |
| Singh et al. [33] | √ | √ | √ | √ | × | √ |
| Bhalerao et al. [79] | √ | √ | × | Only-ROI | √ | × |
| Shi et al. [80] | √ | Only-ROI | Only-ROI | Only-ROI | × | √ |
| Bamal and Kasana [81] | √ | √ | √ | Only-ROI | √ | × |
| Ren et al. [82] | √ | √ | × | √ | √ | × |
| Palani and Loganathan [83] | √ | √ | √ | √ | × | √ |
| **Our scheme** | √ | Only-ROI | Only-ROI | Only-ROI | ROI & RONI | √ |

**Table 5.** Comparisons table for various techniques, performance, and limitations of several watermarking schemes.

| Schemes | Objectives | Method used | Embedding capacity (bpp) | PSNR Embedding (dB) | PSNR Recovery (dB) | Limitation |
|---|---|---|---|---|---|---|
| [56] | TD, TL, TR, ED | DE + Modified DE | ≤0.52 | 40–50 | N/A | No robust, limited capacity |
| [57] | TD, TL, TR, ED | DE + 2D-DE + LSB | ≤0.74 | 35–41 | N/A | No robust, limited capacity, reversible only ROI & RONI |
| [52] | TD, TL, TR, ED | Modified DE + DWT | ≤0.50 | ~36 | N/A | Limited capacity, reversible only ROI |
| [67] | TD, TL | Contrast enhancement + LSB | 0.07–1.26 | 19–31 | Not supported | No robust, limited capacity, not recovery, reversible only ROI |
| [68] | TD, TL, TR | LSB | ≤8 | 47–49 | N/A | No robust, not recovery tampered, irreversible |
| [69] | TD, TL, TR | LSB | N/A | 53–56 | N/A | No robust, limited capacity, irreversible |
| [70] | TD, TL, TR | LSB + DCT | N/A | 50–51 | N/A | No robust, limited capacity, irreversible |
| [29] | TD, TL | DCT | ~1.28 | ~44 | Not supported | Limited capacity, not recovery tampered, irreversible |
| [32] | TD, TL, TR | DCT + LSB | N/A | ~38 | N/A | Limited capacity, irreversible |
| [71] | TD, TL | DWT + PSBFO | N/A | 32–36 | Not supported | Limited capacity, not recovery tampered, irreversible |
| [28] | TD, TL, TR | IWT + DCT | N/A | 38–42 | N/A | Limited capacity, irreversible |
| [31] | TD, TL, TR | Replaced Bit Pixel | N/A | ~44 | ≤37 | Limited capacity, irreversible |
| [30] | TD, TL, TR | LSB + DWT | ≤2 | ~44 | N/A | Irreversible |
| [72] | TD, TL, TR | Zero-bit, RS + LWT | ≤0.15 | 47–49 | N/A | Limited capacity, irreversible |
| [73] | TD, TL, TR, ED | IWT | ≤2 | 48–50 | N/A | Irreversible |
| [74] | TD, TR, ED | SVD + LSB | N/A | 47–48 | N/A | Limited capacity, not localization tampered, irreversible |
| [75] | TD, TL, TR, ED | DE + HS | ≤1 | ~60 | N/A | Limited capacity |
| [76] | TD, ED | DCT | ~0.01 | >53 | Not supported | No localization or recovery; irreversible; limited capacity |
| [10] | TD, TL, TR, ED | IWT + LSB + ILC | ≤1.00 | ≤75 | Not supported | Limited capacity, not recovery tampered, irreversible |
| [27] | TD, TL, TR | LSB + chaotic mapping | ≤2.00 | 43–44 | 30–43 | Limited capacity, irreversible |
| [77] | TD, TL, TR | LSB + chaotic mapping | ≤2.00 | 43–44 | 29–44 | Limited capacity, irreversible |
| [78] | TD | SURF + WDs | N/A | 60.05 | Not supported | No localization or recovery; irreversible; limited capacity |
| [33] | TD, TL, TR, ED | Adaptive LSB + DWT-SVD | ≤0.03 | 40–55 | 40–53 | Limited capacity, irreversible |
| [79] | TD, TR | PEE + Histogram Shifting | ~0.15 | ~55 | N/A | No localization; not robust; limited capacity |
| [80] | TD, TL, TR, ED | Cross-embedding | ~1.50 | ~44.43 | ~53 | Low recovery quality; irreversible; high complexity |
| [81] | TD, TL, TR, ED | RS vector + SLT | ~1.23 | >50 | N/A | Low localization accuracy; poor recovery quality |
| [82] | TD, TR, ED | POB number | ~2.00 | 8 | 8 | No localization; not robust; generates multiple images |
| [83] | TD, TL, TR, ED | DWT + SVD | ~1.50 | ~56 | >56 | High computational complexity; not reversible |
| **Our scheme** | TD, TL, TR, ED | Multi-layer DE + 2D-DE + LSB | ≤6.00 | 35–53 | 40–48 | Reversible only ROI & RONI |

## 5. Conclusion

This paper presented a reversible watermarking scheme specifically designed for medical images, integrating high-capacity data embedding with image authentication, tamper detection, localization, and recovery. The method classifies the image into ROI, RONI, and border regions, applying a multi-layer DE scheme for reversible embedding in the ROI, a 2D-DE approach for semi-fragile embedding in the RONI, and LSB-based embedding for auxiliary data in the border.

Experimental results on MRI, ultrasound, and X-ray images confirm that the proposed method can reliably embed patient records of up to 10 kB using only 12% of the image as ROI while preserving diagnostic quality. The watermarked images consistently achieve high imperceptibility, with average PSNR values above 38 dB and SSIM values close to 1.00. All watermarked images are perfectly restored (excluding the non-reversible border), demonstrating the full reversibility of the ROI and RONI embedding processes. The scheme further provides strong security and integrity verification. Hash-based authentication successfully detects manipulation within the ROI, while the semi-fragile RONI embedding allows precise localization of tampered areas. Recovery performance is also effective: corrupted ROI blocks were reconstructed using the embedded compressed data, achieving quality improvements of up to +28.14 dB relative to the tampered input. In terms of capacity, the proposed method achieves a theoretical embedding capability of 6 bpp in the ROI, outperforming several existing methods. Its adaptability to different image sizes, ROI percentages, and payloads demonstrates its flexibility for practical deployment. Because the ROI recovery relies on lossy-compressed data, the reversibility of the ROI and the correct extraction of the embedded patient record $D$ are guaranteed only when the ROI has not been tampered. When tampering occurs, the reconstructed ROI is visually accurate but not bitwise identical to the original, causing the patient information $D$ to become partially or fully unrecoverable and therefore marked as invalid during extraction. This limitation highlights the need for further research into lossless or hybrid recovery strategies to achieve fully reversible ROI restoration under tampering conditions.

Overall, the proposed watermarking framework offers a secure, reversible, and high-capacity solution for embedding patient information in medical images. It maintains clinical image quality, ensures data confidentiality and integrity, and provides reliable tamper detection and recovery, making it highly suitable for secure telemedicine applications and healthcare information systems.

## CRediT authorship contribution statement

- **Aulia Arham:** Writing - review & editing, Writing - original draft, Visualization, Software, Methodology, Investigation, Formal analysis, Data curation, Conceptualization.
- **Teguh Bharata Adji:** Writing - review & editing, Visualization, Data curation.
- **Syukron Abu Ishaq Alfarozi:** Writing - review & editing, Visualization, Data curation.
- **Hanung Adi Nugroho:** Writing - review & editing, Supervision, Project administration, Methodology, Funding acquisition, Conceptualization.

## Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## Acknowledgments

This work was supported by the Indonesia Endowment Fund for Education (LPDP), Ministry of Finance, Republic of Indonesia.

## Data availability

https://github.com/4rh4m/Reversible-Medical-Image-Watermarking.

## References

[1] K.-H. Chiang, K.-C. Chang-Chien, R.-F. Chang, H.-Y. Yen, Tamper detection and restoring system for medical images using wavelet-based reversible data embedding, J. Digit. Imaging 21 (1) (2008) 77-90, http://dx.doi.org/10.1007/s10278-007-9012-0.

[2] C.-C. Lo, Y.-C. Hu, A novel reversible image authentication scheme for digital images, Signal Process. 98 (2014) 174-185, http://dx.doi.org/10.1016/j.sigpro.2013.11.028.

[3] T. Haridas, S. Upasana, G. Vyshnavi, M.S. Krishnan, S.S. Muni, Chaos-based audio encryption: Efficacy of 2D and 3D hyperchaotic systems, Frankl. Open 8 (2024) 100158, http://dx.doi.org/10.1016/j.fraope.2024.100158.

[4] A. Arham, H.A. Nugroho, T.B. Adji, Multiple layer data hiding scheme based on difference expansion of quad, Signal Process. 137 (2017) 52-62, http://dx.doi.org/10.1016/j.sigpro.2017.02.001.

[5] W. Wang, A reversible data hiding algorithm based on bidirectional difference expansion, Multimedia Tools Appl. 79 (9) (2020) 5965-5988, http://dx.doi.org/10.1007/s11042-019-08255-z.

[6] A. Arham, S.A.I. Alfarozi, H.A. Nugroho, A high-capacity reversible watermarking technique using bit-level expansion and pixel shifting, Commun. Sci. Technol. 10 (2) (2025) 477-492, http://dx.doi.org/10.21924/cst.10.2.2025.1856.

[7] A. Arham, N. Lestari, Secure medical image watermarking based on reversible data hiding with Arnold's cat map, Int. J. Adv. Intell. Informatics 9 (3) (2023) http://dx.doi.org/10.26555/ijain.v9i3.1029.

[8] A. Arham, N. Lestari, Arnold's cat map secure multiple-layer reversible watermarking, Indones. J. Electr. Eng. Comput. Sci. 33 (3) (2024) 1536, http://dx.doi.org/10.11591/ijeecs.v33.i3.

[9] K. Balasamy, S. Suganyadevi, A fuzzy based ROI selection for encryption and watermarking in medical image using DWT and SVD, Multimedia Tools Appl. 80 (5) (2021) 7167-7186, http://dx.doi.org/10.1007/s11042-020-09981-5.

[10] M. Nazari, M. Mehrabian, A novel chaotic IWT-LSB blind watermarking approach with flexible capacity for secure transmission of authenticated medical images, Multimedia Tools Appl. 80 (7) (2021) 10615-10655, http://dx.doi.org/10.1007/s11042-020-10032-2.

[11] A. Arham, H.A. Nugroho, Block-based optimization for enhancing reversible watermarking using reduce difference expansion, Commun. Sci. Technol. 9 (1) (2024) 57-64, http://dx.doi.org/10.21924/cst.9.1.2024.1368.

[12] C.C. Islamy, T. Ahmad, R.M. Ijtihadie, Reversible data hiding based on histogram and prediction error for sharing secret data, Cybersecurity 6 (1) (2023) 12, http://dx.doi.org/10.1186/s42400-023-00147-y.

[13] E.E.-D. Hemdan, An efficient and robust watermarking approach based on single value decompression, multi-level DWT, and wavelet fusion with scrambled medical images, Multimedia Tools Appl. 80 (2) (2021) 1749-1777, http://dx.doi.org/10.1007/s11042-020-09769-7.

[14] A. Al-Haj, H. Abdel-Nabi, An efficient watermarking algorithm for medical images, Multimedia Tools Appl. 80 (17) (2021) 26021-26047, http://dx.doi.org/10.1007/s11042-021-10801-7.

[15] R. Thanki, S. Borra, Fragile watermarking for copyright authentication and tamper detection of medical images using compressive sensing (CS) based encryption and contourlet domain processing, Multimedia Tools Appl. 78 (10) (2019) 13905-13924, http://dx.doi.org/10.1007/s11042-018-6746-2.

[16] R. Thanki, A. Kothari, Multi-level security of medical images based on encryption and watermarking for telemedicine applications, Multimedia Tools Appl. 80 (3) (2021) 4307-4325, http://dx.doi.org/10.1007/s11042-020-09941-z.

[17] A.K. Singh, Robust and distortion control dual watermarking in LWT domain using DCT and error correction code for color medical image, Multimedia Tools Appl. 78 (21) (2019) 30523-30533, http://dx.doi.org/10.1007/s11042-018-7115-x.

[18] A. Arham, H.A. Nugroho, Enhanced reversible data hiding using difference expansion and modulus function with selective bit blocks in images, Cybersecurity 4 (2) (2024) 100-110, http://dx.doi.org/10.1186/s42400-024-00251-7.

[19] M. Moniruzzaman, M.A.K. Hawlader, M.F. Hossain, An image fragile watermarking scheme based on chaotic system for image tamper detection, in: 2014 International Conference on Informatics, Electronics & Vision, ICIEV, IEEE, 2014, pp. 1-6, http://dx.doi.org/10.1109/ICIEV.2014.6850866.

[20] W. Stallings, Cryptography and Network Security, 4th ed., Prentice-Hall, Inc., USA, 2005.

[21] J.M. Zain, L.P. Baldwin, M. Clarke, Reversible watermarking for authentication of DICOM images, in: The 26th Annual International Conference of the IEEE Engineering in Medicine and Biology Society, IEEE, 2004, pp. 3237-3240, http://dx.doi.org/10.1109/IEMBS.2004.1403911.

[22] S.-H. Liu, H.-X. Yao, W. Gao, Y.-L. Liu, An image fragile watermark scheme based on chaotic image pattern and pixel-pairs, Appl. Math. Comput. 185 (2) (2007) 869-882, http://dx.doi.org/10.1016/j.amc.2006.07.036.

[23] S.A. Parah, J.A. Sheikh, F. Ahad, N.A. Loan, G.M. Bhat, Information hiding in medical images: a robust medical image watermarking system for E-healthcare, Multimedia Tools Appl. 76 (8) (2017) 10599-10633, http://dx.doi.org/10.1007/s11042-015-3127-y.

[24] K. Swaraja, Medical image region based watermarking for secured telemedicine, Multimedia Tools Appl. 77 (21) (2018) 28249-28280, http://dx.doi.org/10.1007/s11042-018-6020-7.

[25] F. Sabbane, H. Tairi, Medical image watermarking technique based on polynomial decomposition, Multimedia Tools Appl. 78 (23) (2019) 34129-34155, http://dx.doi.org/10.1007/s11042-019-08134-7.

[26] S. Rawat, B. Raman, A chaotic system based fragile watermarking scheme for image tamper detection, AEU - Int. J. Electron. Commun. 65 (10) (2011) 840-847, http://dx.doi.org/10.1016/j.aeue.2011.01.016.

[27] M. Hussan, S.A. Parah, S. Gull, G. Qureshi, Tamper detection and self-recovery of medical imagery for smart health, Arab. J. Sci. Eng. 46 (2021) 3465-3481, http://dx.doi.org/10.1007/s13369-020-05135-9.

[28] N. Sivasubramanian, G. Konganathan, A novel semi fragile watermarking technique for tamper detection and recovery using IWT and DCT, Computing 102 (6) (2020) 1365-1384, http://dx.doi.org/10.1007/s00607-020-00797-7.

[29] M.J. Barani, M.Y. Valandar, P. Ayubi, A new digital image tamper detection algorithm based on integer wavelet transform and secured by encrypted authentication sequence with 3D quantum map, Optik 187 (2019) 205-222, http://dx.doi.org/10.1016/j.ijleo.2019.04.074.

[30] D. Sarkar, S. Palit, S. Som, K. Dey, Large scale image tamper detection and restoration, Multimedia Tools Appl. 79 (2020) 17761-17791, http://dx.doi.org/10.1007/s11042-020-08669-0.

[31] J. Molina-Garcia, B.P. Garcia-Salgado, V. Ponomaryov, R. Reyes-Reyes, S. Sadovnychiy, C. Cruz-Ramos, An effective fragile watermarking scheme for color image tampering detection and self-recovery, Signal Process., Image Commun. 81 (2020) 115725, http://dx.doi.org/10.1016/j.image.2019.115725.

[32] A. Abdelhakim, H.I. Saleh, M. Abdelhakim, Fragile watermarking for image tamper detection and localization with effective recovery capability using K-means clustering, Multimedia Tools Appl. 78 (2019) 32523-32563, http://dx.doi.org/10.1007/s11042-019-07986-3.

[33] P. Singh, K.J. Devi, H.K. Thakkar, K. Kotecha, Region-based hybrid medical image watermarking scheme for robust and secured transmission in IoMT, IEEE Access 10 (2022) 8974-8993, http://dx.doi.org/10.1109/ACCESS.2022.3143801.

[34] T. Nedelcu, D. Coltuc, Alternate embedding method for difference expansion reversible watermarking, in: 2015 International Symposium on Signals, Circuits and Systems, ISSCS, IEEE, 2015, pp. 1-4, http://dx.doi.org/10.1109/ISSCS.2015.7204017.

[35] O.M. Al-Qershi, B.E. Khoo, Reversible watermarking scheme based on two-dimensional difference expansion (2D-DE), in: 2010 Second International Conference on Computer Research and Development, IEEE, 2010, pp. 228-232, http://dx.doi.org/10.1109/ICCRD.2010.76.

[36] A.M. Alattar, Reversible watermark using difference expansion of triplets, in: Proceedings 2003 International Conference on Image Processing (Cat. No. 03CH37429), Vol. 4, IEEE, 2003, pp. I-501-4, http://dx.doi.org/10.1109/ICIP.2003.1247008.

[37] A.M. Alattar, Reversible watermark using difference expansion of quads, in: 2004 IEEE International Conference on Acoustics, Speech, and Signal Processing, Vol. 3, IEEE, 2004, pp. iii-377-80, http://dx.doi.org/10.1109/ICASSP.2004.1326560.

[38] A.M. Alattar, Reversible watermark using the difference expansion of a generalized integer transform, IEEE Trans. Image Process. 13 (8) (2004) 1147-1156, http://dx.doi.org/10.1109/TIP.2004.828418.

[39] A. Al-Jaber, M.K. Yaqub, Reversible watermarking using modified difference expansion, Int. J. Comput. Inf. Sci. 4 (3) (2006) 134.

[40] I.-C. Dragoi, D. Coltuc, Local-prediction-based difference expansion reversible watermarking, IEEE Trans. Image Process. 23 (4) (2014) 1779-1790, http://dx.doi.org/10.1109/TIP.2014.2307482.

[41] M. Kumar, H. Agarwal, Reversible watermarking scheme for medical images, in: 2014 International Conference on Issues and Challenges in Intelligent Computing Techniques, ICICT, IEEE, 2014, pp. 844-847, http://dx.doi.org/10.1109/ICICICT.2014.6781390.

[42] O.M. Al-Qershi, B.E. Khoo, Two-dimensional difference expansion (2D-DE) scheme with a characteristics-based threshold, Signal Process. 93 (1) (2013) 154-162, http://dx.doi.org/10.1016/j.sigpro.2012.07.012.

[43] P.V. Sabeen Govind, B.M. Varghese, M.V. Judy, A high imperceptible data hiding technique using quorum function, Multimedia Tools Appl. 80 (13) (2021) 20527-20545, http://dx.doi.org/10.1007/s11042-021-10780-9.

[44] T.-C. Lu, Y.-C. Lu, T.N. Vo, Dual-image based high image quality reversible hiding scheme with multiple folding zones, Multimedia Tools Appl. 78 (24) (2019) 34397-34435, http://dx.doi.org/10.1007/s11042-019-07904-7.

[45] D. Huang, J. Wang, Efficient reversible data hiding based on the histogram modification of differences of pixel differences, Multimedia Tools Appl. 79 (29) (2020) 20881-20896, http://dx.doi.org/10.1007/s11042-020-08623-0.

[46] P.C. Mandal, I. Mukherjee, B.N. Chatterji, High capacity reversible and secured data hiding in images using interpolation and difference expansion technique, Multimedia Tools Appl. 80 (3) (2021) 3623-3644, http://dx.doi.org/10.1007/s11042-020-09341-3.

[47] A. Mehbodniya, B. Karimi Douraki, J.L. Webber, H.A. Alkhazaleh, E. Elbasi, M. Dameshghi, R. Abu Zitar, L. Abualigah, Multilayer reversible data hiding based on the difference expansion method using multilevel thresholding of host images based on the slime mould algorithm, Processes 10 (5) (2022) 858, http://dx.doi.org/10.3390/pr10050858.

[48] Q. Zhang, X. Song, T. Wen, C. Fu, Reversible data hiding for 3D mesh models with hybrid prediction and multilayer strategy, Multimedia Tools Appl. 78 (21) (2019) 29713-29729, http://dx.doi.org/10.1007/s11042-018-6219-7.

[49] A. Arham, H.A. Nugroho, T.B. Adji, Combination schemes Reversible Data Hiding for medical images, in: 2016 2nd International Conference on Science and Technology-Computer, ICST, IEEE, 2016, pp. 44-49, http://dx.doi.org/10.1109/ICSTC.2016.7877345.

[50] A. Arham, O.S. Riza, Reversible data hiding using hybrid method of difference expansion on medical image, J. Ilm. Tek. Elektro Komput. Dan Inform. (JITEKI) 6 (2) (2020) 11-19, http://dx.doi.org/10.26555/jiteki.v6i2.16965.

[51] C.K. Tan, J.C. Ng, X. Xu, C.L. Poh, Y.L. Guan, K. Sheah, Security protection of DICOM medical images using dual-layer reversible watermarking with tamper detection capability, J. Digit. Imaging 24 (3) (2011) 528-540, http://dx.doi.org/10.1007/s10278-010-9295-4.

[52] O.M. Al-Qershi, B.E. Khoo, Authentication and data hiding using a hybrid ROI-based watermarking scheme for DICOM images, J. Digit. Imaging 24 (1) (2011) 114-125, http://dx.doi.org/10.1007/s10278-009-9253-1.

[53] S. Kiatpapan, T. Kondo, An image tamper detection and recovery method based on self-embedding dual watermarking, in: 2015 12th International Conference on Electrical Engineering/Electronics, Computer, Telecommunications and Information Technology, ECTI-CON, IEEE, 2015, pp. 1-6, http://dx.doi.org/10.1109/ECTICon.2015.7206973.

[54] J.M. Zain, A.R. Fauzi, Medical image watermarking with tamper detection and recovery, in: 2006 International Conference of the IEEE Engineering in Medicine and Biology Society, IEEE, 2006, pp. 3270-3273, http://dx.doi.org/10.1109/IEMBS.2006.260767.

[55] D.-C. Lou, M.-C. Hu, J.-L. Liu, Multiple layer data hiding scheme for medical images, Comput. Stand. Interfaces 31 (2) (2009) 329-335, http://dx.doi.org/10.1016/j.csi.2008.05.009.

[56] O.M. Al-Qershi, B. Khoo, Authentication and data hiding using a reversible ROI-based watermarking scheme for DICOM images, in: Proceedings of International Conference on Medical Systems Engineering, ICMSE, Citeseer, 2009, pp. 829-834.

[57] O.M. Al-Qershi, B.E. Khoo, ROI-based tamper detection and recovery for medical images using reversible watermarking technique, in: 2010 IEEE International Conference on Information Theory and Information Security, IEEE, 2010, pp. 151-155, http://dx.doi.org/10.1109/ICITIS.2010.5688743.

[58] G. Coatrieux, L. Lecornu, B. Sankur, C. Roux, A review of image watermarking applications in healthcare, in: 2006 International Conference of the IEEE Engineering in Medicine and Biology Society, IEEE, 2006, pp. 4691-4694, http://dx.doi.org/10.1109/IEMBS.2006.259305.

[59] T. Janani, Y. Darak, M. Brindha, Secure similar image search and copyright protection over encrypted medical image databases, IRBM 42 (2) (2021) 83-93, http://dx.doi.org/10.1016/j.irbm.2020.02.005.

[60] R. Sinhal, S. Sharma, I.A. Ansari, V. Bajaj, Multipurpose medical image watermarking for effective security solutions, Multimedia Tools Appl. 81 (10) (2022) 14045-14063, http://dx.doi.org/10.1007/s11042-022-12082-0.

[61] N.A. Memon, A. Alzahrani, Prediction-based reversible watermarking of CT scan images for content authentication and copyright protection, IEEE Access 8 (2020) 75448-75462, http://dx.doi.org/10.1109/ACCESS.2020.2989175.

[62] P. Singh, K.J. Devi, H.K. Thakkar, M. Bilal, A. Nayyar, D. Kwak, Robust and secure medical image watermarking for edge-enabled e-healthcare, IEEE Access 11 (2023) 135831-135845, http://dx.doi.org/10.1109/ACCESS.2023.3335172.

[63] C.-L. Liu, D.-C. Lou, C.-C. Lee, Reversible data embedding using reduced difference expansion, in: Third International Conference on Intelligent Information Hiding and Multimedia Signal Processing, vol. 1, IEEE, 2007, pp. 433-436, http://dx.doi.org/10.1109/IIH-MSP.2007.267.

[64] H. Yi, S. Wei, H. Jianjun, Improved reduced difference expansion based reversible data hiding scheme for digital images, in: 2009 9th International Conference on Electronic Measurement & Instruments, IEEE, 2009, pp. 4-315, http://dx.doi.org/10.1109/ICEMI.2009.5274054.

[65] J. Tian, Reversible data embedding using a difference expansion, IEEE Trans. Circuits Syst. Video Technol. 13 (8) (2003) 890-896, http://dx.doi.org/10.1109/TCSVT.2003.815962.

[66] Emicrobes Digital Library, Partners infectious diseases images, 2024, URL http://www.idimages.org/images/browse/ImageTechnique/.

[67] G. Gao, X. Wan, S. Yao, Z. Cui, C. Zhou, X. Sun, Reversible data hiding with contrast enhancement and tamper localization for medical images, Inform. Sci. 385-386 (2017) 250-265, http://dx.doi.org/10.1016/j.ins.2017.01.009.

[68] H.L. Khor, S.-C. Liew, J.M. Zain, Region of interest-based tamper detection and lossless recovery watermarking scheme (ROI-DR) on ultrasound medical images, J. Digit. Imaging 30 (3) (2017) 328-349, http://dx.doi.org/10.1007/s10278-016-9930-9.

[69] K. Chaitanya, K. Gangadhara Rao, A novel approach to medical image watermarking for tamper detection and recovery of Region of Interest using block compression and checksum, Int. J. Eng. Technology (UAE) 7 (4) (2018) 2137-2148, http://dx.doi.org/10.14419/ijet.v7i4.128554.

[70] K. Chaitanya, K.G. Rao, A novel approach to medical image watermarking for tamper detection and recovery of region of interest using predictive coding and hashing, J. Theor. Appl. Inf. Technol. 96 (7) (2018).

[71] K. Swaraja, K. Meenakshi, P. Kora, An optimized blind dual medical image watermarking framework for tamper localization and content authentication in secured telemedicine, Biomed. Signal Process. Control. 55 (2020) 101665, http://dx.doi.org/10.1016/j.bspc.2019.101665.

[72] N.E.H. Golea, K.E. Melkemi, A. Behloul, Zero-bit fragile watermarking for medical image tamper detection and recovery using RS code and lifting wavelet transform, Imaging Sci. J. 69 (5-8) (2021) 334-349, http://dx.doi.org/10.1080/13682199.2022.2161144.

[73] D. Ravichandran, P. Praveenkumar, S. Rajagopalan, J.B.B. Rayappan, R. Amirtharajan, ROI-based medical image watermarking for accurate tamper detection, localisation and recovery, Med. Biol. Eng. Comput. 59 (6) (2021) 1355-1372, http://dx.doi.org/10.1007/s11517-021-02374-2.

[74] H.S. Alshanbari, Medical image watermarking for ownership & tamper detection, Multimedia Tools Appl. 80 (11) (2021) 16549-16564, http://dx.doi.org/10.1007/s11042-020-08814-9.

[75] H. Shi, Y. Wang, Y. Li, Y. Ren, C. Guo, Region-based reversible medical image watermarking algorithm for privacy protection and integrity authentication, Multimedia Tools Appl. 80 (16) (2021) 24631-24667, http://dx.doi.org/10.1007/s11042-021-10853-9.

[76] D. Laishram, K. Manglem Singh, A watermarking scheme for source authentication, ownership identification, tamper detection and restoration for color medical images, Multimedia Tools Appl. 80 (16) (2021) 23815-23875, http://dx.doi.org/10.1007/s11042-020-10389-4.

[77] M. Hussan, S.A. Parah, A. Jan, G. Qureshi, Self-embedding framework for tamper detection and restoration of color images, Multimedia Tools Appl. 81 (13) (2022) 18563-18594, http://dx.doi.org/10.1007/s11042-022-12545-4.

[78] A. Soualmi, A. Alti, L. Laouamer, An imperceptible watermarking scheme for medical image tamper detection, Int. J. Inf. Secur. Priv. 16 (1) (2022) http://dx.doi.org/10.4018/IJISP.2022010102.

[79] S. Bhalerao, I.A. Ansari, A. Kumar, A reversible medical image watermarking for ROI tamper detection and recovery, Circuits Systems Signal Process. 42 (11) (2023) 6701-6725, http://dx.doi.org/10.1007/s00034-023-02416-0.

[80] H. Shi, K. Yan, J. Geng, Y. Ren, A cross-embedding based medical image tamper detection and self-recovery watermarking scheme, Multimedia Tools Appl. 83 (10) (2024) 30319-30360, http://dx.doi.org/10.1007/s11042-023-16679-x.

[81] R. Bamal, S.S. Kasana, Reversible medical image watermarking for tamper detection using ANN and SLT, Multimedia Tools Appl. 83 (8) (2024) 21849-21882, http://dx.doi.org/10.1007/s11042-023-14737-y.

[82] F. Ren, X. Shi, E. Tang, M. Zeng, Data hiding and authentication scheme for medical images using double POB, Appl. Sci. (Switzerland) 14 (6) (2024) http://dx.doi.org/10.3390/app14062664.

[83] A. Palani, A. Loganathan, Semi-Blind watermarking using convolutional attention-based turtle shell matrix for tamper detection and recovery of medical images, Expert Syst. Appl. 238 (2024) 121903, http://dx.doi.org/10.1016/j.eswa.2023.121903.

## Author biographies

**Aulia Arham** received the B.Sc. degree in Informatics Engineering from Sekolah Tinggi Manajemen Informatika dan Komputer Duta Bangsa (STMIKDB), Surakarta, Indonesia, and the M.S. degree in Electrical Engineering from Universitas Gadjah Mada, Yogyakarta, Indonesia, in 2016. Since 2018, he has been a lecturer in the Department of Information Systems, Faculty of Science and Technology, Universitas Islam Negeri Imam Bonjol, Padang, Indonesia. He is currently pursuing the Ph.D. degree with the Department of Electrical and Information Engineering. His research interests include watermarking, steganography, cryptography, security, image processing, and medical imaging.

**Teguh Bharata Adji** received his Bachelor of Engineering degree from Universitas Gadjah Mada, Indonesia, in 1995, his Master of Electrical Engineering degree from Universitas Gadjah Mada, Indonesia, in 2001, and his Master of Applied Mathematical Engineering degree from Doshisha University, Japan, in 2001. He also earned his Doctor of Philosophy degree in Electrical and Electronics Engineering from Universiti Teknologi Petronas, Seri Iskandar, Malaysia, in 2010. Currently, he works in the Department of Electrical Engineering and Information Technology at Universitas Gadjah Mada, Indonesia. His current research interests include Artificial Intelligence, Parallel Computing, Algorithms, Computer Node Balancing, and Embedded Systems.

**Syukron Abu Ishaq Alfarozi** received the bachelor's (S.T.) degree in Electrical and Information Engineering from Universitas Gadjah Mada (UGM), Yogyakarta, Indonesia, in 2014, and the Ph.D. degree in Information Technology from King Mongkut's Institute of Technology Ladkrabang, Bangkok, Thailand, under the sandwich program with Hokkaido University, Sapporo, Japan, in 2020. He is currently with the Department of Electrical and Information Engineering, Faculty of Engineering, UGM. His research interests include machine learning and its applications, computer vision, and signal processing.

**Hanung Adi Nugroho** received the bachelor's degree in Electrical Engineering from the Department of Electrical and Information Engineering, Universitas Gadjah Mada, Yogyakarta, in 2001, the M.Eng. degree in Biomedical Engineering from The University of Queensland, Australia, in 2005, and the Ph.D. degree in Electrical Engineering from Universiti Teknologi PETRONAS, Malaysia, in 2012. He is currently a Professor with the Department of Electrical and Information Engineering, Faculty of Engineering, Universitas Gadjah Mada. His current research interests include biomedical signal and image processing and analysis, computer vision, medical instrumentation, and pattern recognition.