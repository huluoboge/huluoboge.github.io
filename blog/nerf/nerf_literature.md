# 文献列表

本文档包含以下文献条目：

## 1. Mip-NeRF: A Multiscale Representation for Anti-Aliasing Neural Radiance Fields

**作者**: J. Barron and B. Mildenhall and Matthew Tancik and Peter Hedman and Ricardo Martin-Brualla and Pratul P. Srinivasan

**出处**: 2021 IEEE/CVF International Conference on Computer Vision (ICCV), 2021, 卷 null, 页 5835-5844

**链接**: [原文链接](https://www.semanticscholar.org/paper/21336e57dc2ab9ae2171a0f6c35f7d1aba584796) | [DOI](https://doi.org/10.1109/ICCV48922.2021.00580) | [arXiv](https://arxiv.org/abs/2103.13415)

**摘要**: The rendering procedure used by neural radiance fields (NeRF) samples a scene with a single ray per pixel and may therefore produce renderings that are excessively blurred or aliased when training or testing images observe scene content at different resolutions. The straightforward solution of supersampling by rendering with multiple rays per pixel is impractical for NeRF, because rendering each ray requires querying a multilayer perceptron hundreds of times. Our solution, which we call "mip-NeRF" (à la "mipmap"), extends NeRF to represent the scene at a continuously-valued scale. By efficiently rendering anti-aliased conical frustums instead of rays, mip-NeRF reduces objectionable aliasing artifacts and significantly improves NeRF’s ability to represent fine details, while also being 7% faster than NeRF and half the size. Compared to NeRF, mip-NeRF reduces average error rates by 17% on the dataset presented with NeRF and by 60% on a challenging multiscale variant of that dataset that we present. Mip-NeRF is also able to match the accuracy of a brute-force supersampled NeRF on our multiscale dataset while being 22× faster.

---

## 2. ScanNeRF: a Scalable Benchmark for Neural Radiance Fields

**作者**: Luca De Luigi and Damiano Bolognini and Federico Domeniconi and Daniele De Gregorio and Matteo Poggi and L. D. Stefano

**出处**: 2023 IEEE/CVF Winter Conference on Applications of Computer Vision (WACV), 2022, 卷 null, 页 816-825

**链接**: [原文链接](https://www.semanticscholar.org/paper/c751c9edfcfc62cdb40c3a6c652708ef05302e24) | [DOI](https://doi.org/10.1109/WACV56688.2023.00088) | [arXiv](https://arxiv.org/abs/2211.13762)

**摘要**: In this paper, we propose the first-ever real benchmark thought for evaluating Neural Radiance Fields (NeRFs) and, in general, Neural Rendering (NR) frameworks. We design and implement an effective pipeline for scanning real objects in quantity and effortlessly. Our scan station is built with less than 500$ hardware budget and can collect roughly 4000 images of a scanned object in just 5 minutes. Such a platform is used to build ScanNeRF, a dataset characterized by several train/val/test splits aimed at benchmarking the performance of modern NeRF methods under different conditions. Accordingly, we evaluate three cuttingedge NeRF variants on it to highlight their strengths and weaknesses. The dataset is available on our project page, together with an online benchmark to foster the development of better and better NeRFs.

---

## 3. Volume Rendering of Neural Implicit Surfaces

**作者**: Lior Yariv and Jiatao Gu and Yoni Kasten and Y. Lipman

**出处**: 2021

**链接**: [原文链接](https://www.semanticscholar.org/paper/eded1f3acaba853499fd5a6b3de63fa9d5e0cef2) | [arXiv](https://arxiv.org/abs/2106.12052)

**摘要**: Neural volume rendering became increasingly popular recently due to its success in synthesizing novel views of a scene from a sparse set of input images. So far, the geometry learned by neural volume rendering techniques was modeled using a generic density function. Furthermore, the geometry itself was extracted using an arbitrary level set of the density function leading to a noisy, often low fidelity reconstruction. The goal of this paper is to improve geometry representation and reconstruction in neural volume rendering. We achieve that by modeling the volume density as a function of the geometry. This is in contrast to previous work modeling the geometry as a function of the volume density. In more detail, we define the volume density function as Laplace's cumulative distribution function (CDF) applied to a signed distance function (SDF) representation. This simple density representation has three benefits: (i) it provides a useful inductive bias to the geometry learned in the neural volume rendering process; (ii) it facilitates a bound on the opacity approximation error, leading to an accurate sampling of the viewing ray. Accurate sampling is important to provide a precise coupling of geometry and radiance; and (iii) it allows efficient unsupervised disentanglement of shape and appearance in volume rendering. Applying this new density representation to challenging scene multiview datasets produced high quality geometry reconstructions, outperforming relevant baselines. Furthermore, switching shape and appearance between scenes is possible due to the disentanglement of the two.

---

## 4. 3D Gaussian Splatting for Real-Time Radiance Field Rendering

**作者**: Bernhard Kerbl and Georgios Kopanas and Thomas Leimkuehler and G. Drettakis

**出处**: ACM Transactions on Graphics (TOG), 2023, 卷 42, 页 1 - 14

**链接**: [原文链接](https://www.semanticscholar.org/paper/2cc1d857e86d5152ba7fe6a8355c2a0150cc280a) | [DOI](https://doi.org/10.1145/3592433) | [arXiv](https://arxiv.org/abs/2308.04079)

**摘要**: Radiance Field methods have recently revolutionized novel-view synthesis of scenes captured with multiple photos or videos. However, achieving high visual quality still requires neural networks that are costly to train and render, while recent faster methods inevitably trade off speed for quality. For unbounded and complete scenes (rather than isolated objects) and 1080p resolution rendering, no current method can achieve real-time display rates. We introduce three key elements that allow us to achieve state-of-the-art visual quality while maintaining competitive training times and importantly allow high-quality real-time (≥ 30 fps) novel-view synthesis at 1080p resolution. First, starting from sparse points produced during camera calibration, we represent the scene with 3D Gaussians that preserve desirable properties of continuous volumetric radiance fields for scene optimization while avoiding unnecessary computation in empty space; Second, we perform interleaved optimization/density control of the 3D Gaussians, notably optimizing anisotropic covariance to achieve an accurate representation of the scene; Third, we develop a fast visibility-aware rendering algorithm that supports anisotropic splatting and both accelerates training and allows realtime rendering. We demonstrate state-of-the-art visual quality and real-time rendering on several established datasets.

---

## 5. Nerfies: Deformable Neural Radiance Fields

**作者**: Keunhong Park and U. Sinha and J. Barron and Sofien Bouaziz and Dan B. Goldman and S. Seitz and Ricardo Martin-Brualla

**出处**: 2021 IEEE/CVF International Conference on Computer Vision (ICCV), 2020, 卷 null, 页 5845-5854

**链接**: [原文链接](https://www.semanticscholar.org/paper/0f1af3f94f4699cd70a554f68f8f9e2c8e3d53dd) | [DOI](https://doi.org/10.1109/ICCV48922.2021.00581) | [arXiv](https://arxiv.org/abs/2011.12948)

**摘要**: We present the first method capable of photorealistically reconstructing deformable scenes using photos/videos captured casually from mobile phones. Our approach augments neural radiance fields (NeRF) by optimizing an additional continuous volumetric deformation field that warps each observed point into a canonical 5D NeRF. We observe that these NeRF-like deformation fields are prone to local minima, and propose a coarse-to-fine optimization method for coordinate-based models that allows for more robust optimization. By adapting principles from geometry processing and physical simulation to NeRF-like models, we propose an elastic regularization of the deformation field that further improves robustness. We show that our method can turn casually captured selfie photos/videos into deformable NeRF models that allow for photorealistic renderings of the subject from arbitrary viewpoints, which we dub "nerfies." We evaluate our method by collecting time-synchronized data using a rig with two mobile phones, yielding train/validation images of the same pose at different viewpoints. We show that our method faithfully reconstructs non-rigidly deforming scenes and reproduces unseen views with high fidelity.

---

## 6. DONeRF: Towards Real‐Time Rendering of Compact Neural Radiance Fields using Depth Oracle Networks

**作者**: Thomas Neff and P. Stadlbauer and Mathias Parger and A. Kurz and J. H. Mueller and C. R. A. Chaitanya and Anton Kaplanyan and M. Steinberger

**出处**: Computer Graphics Forum, 2021, 卷 40, 页 null

**链接**: [原文链接](https://www.semanticscholar.org/paper/792f25e5a2f167df962e0d25b6bee5474a86605f) | [DOI](https://doi.org/10.1111/cgf.14340) | [arXiv](https://arxiv.org/abs/2103.03231)

**摘要**: The recent research explosion around implicit neural representations, such as NeRF, shows that there is immense potential for implicitly storing high‐quality scene and lighting information in compact neural networks. However, one major limitation preventing the use of NeRF in real‐time rendering applications is the prohibitive computational cost of excessive network evaluations along each view ray, requiring dozens of petaFLOPS. In this work, we bring compact neural representations closer to practical rendering of synthetic content in real‐time applications, such as games and virtual reality. We show that the number of samples required for each view ray can be significantly reduced when samples are placed around surfaces in the scene without compromising image quality. To this end, we propose a depth oracle network that predicts ray sample locations for each view ray with a single network evaluation. We show that using a classification network around logarithmically discretized and spherically warped depth values is essential to encode surface locations rather than directly estimating depth. The combination of these techniques leads to DONeRF, our compact dual network design with a depth oracle network as its first step and a locally sampled shading network for ray accumulation. With DONeRF, we reduce the inference costs by up to 48× compared to NeRF when conditioning on available ground truth depth information. Compared to concurrent acceleration methods for raymarching‐based neural representations, DONeRF does not require additional memory for explicit caching or acceleration structures, and can render interactively (20 frames per second) on a single GPU.

---

## 7. Depth-supervised NeRF: Fewer Views and Faster Training for Free

**作者**: Kangle Deng and Andrew Liu and Jun-Yan Zhu and Deva Ramanan

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2021, 卷 null, 页 12872-12881

**链接**: [原文链接](https://www.semanticscholar.org/paper/988952b0e737c8ab9b6c1fbd6d54db86e299d270) | [DOI](https://doi.org/10.1109/CVPR52688.2022.01254) | [arXiv](https://arxiv.org/abs/2107.02791)

**摘要**: A commonly observed failure mode of Neural Radiance Field (NeRF) is fitting incorrect geometries when given an insufficient number of input views. One potential reason is that standard volumetric rendering does not enforce the constraint that most of a scene's geometry consist of empty space and opaque surfaces. We formalize the above assumption through DS-NeRF (Depth-supervised Neural Radiance Fields), a loss for learning radiance fields that takes advantage of readily-available depth supervision. We leverage the fact that current NeRF pipelines require images with known camera poses that are typically estimated by running structure-from-motion (SFM). Crucially, SFM also produces sparse 3D points that can be used as “free” depth supervision during training: we add a loss to encourage the distribution of a ray's terminating depth matches a given 3D keypoint, incorporating depth uncertainty. DS-NeRF can render better images given fewer training views while training 2-3x faster. Further, we show that our loss is compatible with other recently proposed NeRF methods, demonstrating that depth is a cheap and easily digestible supervisory signal. And finally, we find that DS-NeRF can support other types of depth supervision such as scanned depth sensors and RGB-D reconstruction outputs.

---

## 8. FastNeRF: High-Fidelity Neural Rendering at 200FPS

**作者**: Stephan J. Garbin and Marek Kowalski and Matthew Johnson and J. Shotton and Julien P. C. Valentin

**出处**: 2021 IEEE/CVF International Conference on Computer Vision (ICCV), 2021, 卷 null, 页 14326-14335

**链接**: [原文链接](https://www.semanticscholar.org/paper/c0ccfbaf073c91e68ccbc57af2114c72c0d0427d) | [DOI](https://doi.org/10.1109/ICCV48922.2021.01408) | [arXiv](https://arxiv.org/abs/2103.10380)

**摘要**: Recent work on Neural Radiance Fields (NeRF) showed how neural networks can be used to encode complex 3D environments that can be rendered photorealistically from novel viewpoints. Rendering these images is very computationally demanding and recent improvements are still a long way from enabling interactive rates, even on high-end hardware. Motivated by scenarios on mobile and mixed reality devices, we propose FastNeRF, the first NeRF-based system capable of rendering high fidelity photorealistic images at 200Hz on a high-end consumer GPU. The core of our method is a graphics-inspired factorization that allows for (i) compactly caching a deep radiance map at each position in space, (ii) efficiently querying that map using ray directions to estimate the pixel values in the rendered image. Extensive experiments show that the proposed method is 3000 times faster than the original NeRF algorithm and at least an order of magnitude faster than existing work on accelerating NeRF, while maintaining visual quality and extensibility.

---

## 9. Ref-NeRF: Structured View-Dependent Appearance for Neural Radiance Fields

**作者**: Dor Verbin and Peter Hedman and B. Mildenhall and Todd Zickler and J. Barron and Pratul P. Srinivasan

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2021, 卷 null, 页 5481-5490

**链接**: [原文链接](https://www.semanticscholar.org/paper/40c8c8d8a41c16a0e017cc0d059fae9d346795f0) | [DOI](https://doi.org/10.1109/CVPR52688.2022.00541) | [arXiv](https://arxiv.org/abs/2112.03907) | [PMID](https://pubmed.ncbi.nlm.nih.gov/38289850/)

**摘要**: Neural Radiance Fields (NeRF) is a popular view synthesis technique that represents a scene as a continuous volumetric function, parameterized by multilayer perceptrons that provide the volume density and view-dependent emitted radiance at each location. While NeRF-based techniques excel at representing fine geometric structures with smoothly varying view-dependent appearance, they often fail to accurately capture and reproduce the appearance of glossy surfaces. We address this limitation by introducing Ref-NeRF, which replaces NeRF's parameterization of view-dependent outgoing radiance with a representation of reflected radiance and structures this function using a collection of spatially-varying scene properties. We show that together with a regularizer on normal vectors, our model significantly improves the realism and accuracy of specular reflections. Furthermore, we show that our model's internal representation of outgoing radiance is interpretable and useful for scene editing.

---

## 10. Dense Depth Priors for Neural Radiance Fields from Sparse Input Views

**作者**: Barbara Roessle and J. Barron and B. Mildenhall and Pratul P. Srinivasan and M. Nießner

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2021, 卷 null, 页 12882-12891

**链接**: [原文链接](https://www.semanticscholar.org/paper/26b1c7ba30879b54c42eef91ee58fa906d7e26cb) | [DOI](https://doi.org/10.1109/CVPR52688.2022.01255) | [arXiv](https://arxiv.org/abs/2112.03288)

**摘要**: Neural radiance fields (NeRF) encode a scene into a neural representation that enables photo-realistic rendering of novel views. However, a successful reconstruction from RGB images requires a large number of input views taken under static conditions — typically up to a few hundred images for room-size scenes. Our method aims to synthesize novel views of whole rooms from an order of magnitude fewer images. To this end, we leverage dense depth priors in order to constrain the NeRF optimization. First, we take advantage of the sparse depth data that is freely available from the structure from motion (SfM) preprocessing step used to estimate camera poses. Second, we use depth completion to convert these sparse points into dense depth maps and uncertainty estimates, which are used to guide NeRF optimization. Our method enables data-efficient novel view synthesis on challenging indoor scenes, using as few as 18 images for an entire scene.

---

## 11. MVSNeRF: Fast Generalizable Radiance Field Reconstruction from Multi-View Stereo

**作者**: Anpei Chen and Zexiang Xu and Fuqiang Zhao and Xiaoshuai Zhang and Fanbo Xiang and Jingyi Yu and Hao Su

**出处**: 2021 IEEE/CVF International Conference on Computer Vision (ICCV), 2021, 卷 null, 页 14104-14113

**链接**: [原文链接](https://www.semanticscholar.org/paper/169971b60749264cbbe2b577dc4d2ad23ca4f46c) | [DOI](https://doi.org/10.1109/ICCV48922.2021.01386) | [arXiv](https://arxiv.org/abs/2103.15595)

**摘要**: We present MVSNeRF, a novel neural rendering approach that can efficiently reconstruct neural radiance fields for view synthesis. Unlike prior works on neural radiance fields that consider per-scene optimization on densely captured images, we propose a generic deep neural network that can reconstruct radiance fields from only three nearby input views via fast network inference. Our approach leverages plane-swept cost volumes (widely used in multi-view stereo) for geometry-aware scene reasoning, and combines this with physically based volume rendering for neural radiance field reconstruction. We train our network on real objects in the DTU dataset, and test it on three different datasets to evaluate its effectiveness and generalizability. Our approach can generalize across scenes (even indoor scenes, completely different from our training scenes of objects) and generate realistic view synthesis results using only three input images, significantly outperforming concurrent works on generalizable radiance field reconstruction. Moreover, if dense images are captured, our estimated radiance field representation can be easily fine-tuned; this leads to fast per-scene reconstruction with higher rendering quality and substantially less optimization time than NeRF.

---

## 12. D-NeRF: Neural Radiance Fields for Dynamic Scenes

**作者**: Albert Pumarola and Enric Corona and Gerard Pons-Moll and F. Moreno-Noguer

**出处**: 2021 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2020, 卷 null, 页 10313-10322

**链接**: [原文链接](https://www.semanticscholar.org/paper/694bdf6e5906992dad2987a3cc8d1a176de691c9) | [DOI](https://doi.org/10.1109/CVPR46437.2021.01018) | [arXiv](https://arxiv.org/abs/2011.13961)

**摘要**: Neural rendering techniques combining machine learning with geometric reasoning have arisen as one of the most promising approaches for synthesizing novel views of a scene from a sparse set of images. Among these, stands out the Neural radiance fields (NeRF) [31], which trains a deep network to map 5D input coordinates (representing spatial location and viewing direction) into a volume density and view-dependent emitted radiance. However, despite achieving an unprecedented level of photorealism on the generated images, NeRF is only applicable to static scenes, where the same spatial location can be queried from different images. In this paper we introduce D-NeRF, a method that extends neural radiance fields to a dynamic domain, allowing to reconstruct and render novel images of objects under rigid and non-rigid motions from a single camera moving around the scene. For this purpose we consider time as an additional input to the system, and split the learning process in two main stages: one that encodes the scene into a canonical space and another that maps this canonical representation into the deformed scene at a particular time. Both mappings are simultaneously learned using fully-connected networks. Once the networks are trained, D-NeRF can render novel images, controlling both the camera view and the time variable, and thus, the object movement. We demonstrate the effectiveness of our approach on scenes with objects under rigid, articulated and non-rigid motions. Code, model weights and the dynamic scenes dataset will be available at [1].

---

## 13. NeRF++: Analyzing and Improving Neural Radiance Fields

**作者**: Kai Zhang and Gernot Riegler and Noah Snavely and V. Koltun

**出处**: ArXiv, 2020, 卷 abs/2010.07492, 页 null

**链接**: [原文链接](https://www.semanticscholar.org/paper/5b0ea2c92ee16fa2f5a3dbc9315cd5c1e4ec1d88) | [arXiv](https://arxiv.org/abs/2010.07492)

**摘要**: Neural Radiance Fields (NeRF) achieve impressive view synthesis results for a variety of capture settings, including 360 capture of bounded scenes and forward-facing capture of bounded and unbounded scenes. NeRF fits multi-layer perceptrons (MLPs) representing view-invariant opacity and view-dependent color volumes to a set of training images, and samples novel views based on volume rendering techniques. In this technical report, we first remark on radiance fields and their potential ambiguities, namely the shape-radiance ambiguity, and analyze NeRF's success in avoiding such ambiguities. Second, we address a parametrization issue involved in applying NeRF to 360 captures of objects within large-scale, unbounded 3D scenes. Our method improves view synthesis fidelity in this challenging scenario. Code is available at this https URL.

---

## 14. NeuS: Learning Neural Implicit Surfaces by Volume Rendering for Multi-view Reconstruction

**作者**: Peng Wang and Lingjie Liu and Yuan Liu and C. Theobalt and T. Komura and Wenping Wang

**出处**: ArXiv, 2021, 卷 abs/2106.10689, 页 null

**链接**: [原文链接](https://www.semanticscholar.org/paper/cf5647cb2613f5f697729eab567383006dcd4913) | [arXiv](https://arxiv.org/abs/2106.10689)

**摘要**: We present a novel neural surface reconstruction method, called NeuS, for reconstructing objects and scenes with high fidelity from 2D image inputs. Existing neural surface reconstruction approaches, such as DVR and IDR, require foreground mask as supervision, easily get trapped in local minima, and therefore struggle with the reconstruction of objects with severe self-occlusion or thin structures. Meanwhile, recent neural methods for novel view synthesis, such as NeRF and its variants, use volume rendering to produce a neural scene representation with robustness of optimization, even for highly complex objects. However, extracting high-quality surfaces from this learned implicit representation is difficult because there are not sufficient surface constraints in the representation. In NeuS, we propose to represent a surface as the zero-level set of a signed distance function (SDF) and develop a new volume rendering method to train a neural SDF representation. We observe that the conventional volume rendering method causes inherent geometric errors (i.e. bias) for surface reconstruction, and therefore propose a new formulation that is free of bias in the first order of approximation, thus leading to more accurate surface reconstruction even without the mask supervision. Experiments on the DTU dataset and the BlendedMVS dataset show that NeuS outperforms the state-of-the-arts in high-quality surface reconstruction, especially for objects and scenes with complex structures and self-occlusion.

---

## 15. MobileNeRF: Exploiting the Polygon Rasterization Pipeline for Efficient Neural Field Rendering on Mobile Architectures

**作者**: Zhiqin Chen and T. Funkhouser and Peter Hedman and A. Tagliasacchi

**出处**: 2023 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2022, 卷 null, 页 16569-16578

**链接**: [原文链接](https://www.semanticscholar.org/paper/b31c2967451722780e92604532e19cdd3f0f49fb) | [DOI](https://doi.org/10.1109/CVPR52729.2023.01590) | [arXiv](https://arxiv.org/abs/2208.00277)

**摘要**: Neural Radiance Fields (NeRFs) have demonstrated amazing ability to synthesize images of 3D scenes from novel views. However, they rely upon specialized volumetric rendering algorithms based on ray marching that are mismatched to the capabilities of widely deployed graphics hardware. This paper introduces a new NeRF representation based on textured polygons that can synthesize novel images efficiently with standard rendering pipelines. The NeRF is represented as a set of polygons with textures representing binary opacities and feature vectors. Traditional rendering of the polygons with a z-buffer yields an image with features at every pixel, which are interpreted by a small, view-dependent MLP running in a fragment shader to produce a final pixel color. This approach enables NeRFs to be rendered with the traditional polygon rasterization pipeline, which provides massive pixel-level parallelism, achieving interactive frame rates on a wide range of compute platforms, including mobile phones. Project page: https://mobile-nerf.github.io

---

## 16. Fast Dynamic Radiance Fields with Time-Aware Neural Voxels

**作者**: Jiemin Fang and Taoran Yi and Xinggang Wang and Lingxi Xie and Xiaopeng Zhang and Wenyu Liu and M. Nießner and Qi Tian

**出处**: SIGGRAPH Asia 2022 Conference Papers, 2022, 卷 null, 页 null

**链接**: [原文链接](https://www.semanticscholar.org/paper/8f01dff0485488c02b567dac44cdfe9f708cfe70) | [DOI](https://doi.org/10.1145/3550469.3555383) | [arXiv](https://arxiv.org/abs/2205.15285)

**摘要**: Neural radiance fields (NeRF) have shown great success in modeling 3D scenes and synthesizing novel-view images. However, most previous NeRF methods take much time to optimize one single scene. Explicit data structures, e.g. voxel features, show great potential to accelerate the training process. However, voxel features face two big challenges to be applied to dynamic scenes, i.e. modeling temporal information and capturing different scales of point motions. We propose a radiance field framework by representing scenes with time-aware voxel features, named as TiNeuVox. A tiny coordinate deformation network is introduced to model coarse motion trajectories and temporal information is further enhanced in the radiance network. A multi-distance interpolation method is proposed and applied on voxel features to model both small and large motions. Our framework significantly accelerates the optimization of dynamic radiance fields while maintaining high rendering quality. Empirical evaluation is performed on both synthetic and real scenes. Our TiNeuVox completes training with only 8 minutes and 8-MB storage cost while showing similar or even better rendering performance than previous dynamic NeRF methods. Code is available at https://github.com/hustvl/TiNeuVox.

---

## 17. Multiscale Representation for Real-Time Anti-Aliasing Neural Rendering

**作者**: Dongting Hu and Zhenkai Zhang and Tingbo Hou and Tongliang Liu and Huan Fu and Mingming Gong

**出处**: 2023 IEEE/CVF International Conference on Computer Vision (ICCV), 2023, 卷 null, 页 17726-17737

**链接**: [原文链接](https://www.semanticscholar.org/paper/969af2970b58f9d2edc08144fc7493e7c0edb0e5) | [DOI](https://doi.org/10.1109/ICCV51070.2023.01629) | [arXiv](https://arxiv.org/abs/2304.10075)

**摘要**: The rendering scheme in neural radiance field (NeRF) is effective in rendering a pixel by casting a ray into the scene. However, NeRF yields blurred rendering results when the training images are captured at non-uniform scales, and produces aliasing artifacts if the test images are taken in distant views. To address this issue, Mip-NeRF proposes a multiscale representation as a conical frustum to encode scale information. Nevertheless, this approach is only suitable for offline rendering since it relies on integrated positional encoding (IPE) to query a multilayer perceptron (MLP). To overcome this limitation, we propose mip voxel grids (Mip-VoG), an explicit multiscale representation with a deferred architecture for real-time anti-aliasing rendering. Our approach includes a density Mip-VoG for scene geometry and a feature Mip-VoG with a small MLP for view-dependent color. Mip-VoG represents scene scale using the level of detail (LOD) derived from ray differentials and uses quadrilinear interpolation to map a queried 3D location to its features and density from two neighboring down-sampled voxel grids. To our knowledge, our approach is the first to offer multiscale training and real-time anti-aliasing rendering simultaneously. We conducted experiments on multiscale dataset, results show that our approach outperforms state-of-the-art real-time rendering baselines.

---

## 18. Baking Neural Radiance Fields for Real-Time View Synthesis

**作者**: Peter Hedman and Pratul P. Srinivasan and B. Mildenhall and Christian Reiser and Jonathan T. Barron and Paul E. Debevec

**出处**: IEEE Transactions on Pattern Analysis and Machine Intelligence, 2024, 卷 47, 页 3310-3321

**链接**: [原文链接](https://www.semanticscholar.org/paper/085f76d008a11a07347367e6acefa79fdb891a0d) | [DOI](https://doi.org/10.1109/TPAMI.2024.3381001) | [arXiv](https://arxiv.org/abs/2103.14645) | [PMID](https://pubmed.ncbi.nlm.nih.gov/38526902/)

**摘要**: null

---

## 19. Neural Sparse Voxel Fields

**作者**: Lingjie Liu and Jiatao Gu and Kyaw Zaw Lin and Tat-Seng Chua and C. Theobalt

**出处**: ArXiv, 2020, 卷 abs/2007.11571, 页 null

**链接**: [原文链接](https://www.semanticscholar.org/paper/17d7767a6ea87f4ab24d9cfaa5039160af9cad76) | [arXiv](https://arxiv.org/abs/2007.11571)

**摘要**: Photo-realistic free-viewpoint rendering of real-world scenes using classical computer graphics techniques is challenging, because it requires the difficult step of capturing detailed appearance and geometry models. Recent studies have demonstrated promising results by learning scene representations that implicitly encode both geometry and appearance without 3D supervision. However, existing approaches in practice often show blurry renderings caused by the limited network capacity or the difficulty in finding accurate intersections of camera rays with the scene geometry. Synthesizing high-resolution imagery from these representations often requires time-consuming optical ray marching. In this work, we introduce Neural Sparse Voxel Fields (NSVF), a new neural scene representation for fast and high-quality free-viewpoint rendering. NSVF defines a set of voxel-bounded implicit fields organized in a sparse voxel octree to model local properties in each cell. We progressively learn the underlying voxel structures with a diffentiable ray-marching operation from only a set of posed RGB images. With the sparse voxel octree structure, rendering novel views can be accelerated by skipping the voxels containing no relevant scene content. Our method is over 10 times faster than the state-of-the-art (namely, NeRF) at inference time while achieving higher quality results. Furthermore, by utilizing an explicit sparse voxel representation, our method can easily be applied to scene editing and scene composition. We also demonstrate several challenging tasks, including multi-scene learning, free-viewpoint rendering of a moving human, and large-scale scene rendering.

---

## 20. PlenOctrees for Real-time Rendering of Neural Radiance Fields

**作者**: Alex Yu and Ruilong Li and Matthew Tancik and Hao Li and Ren Ng and Angjoo Kanazawa

**出处**: 2021 IEEE/CVF International Conference on Computer Vision (ICCV), 2021, 卷 null, 页 5732-5741

**链接**: [原文链接](https://www.semanticscholar.org/paper/5744fcc21b40327f7ad710de7d947d4584c53012) | [DOI](https://doi.org/10.1109/ICCV48922.2021.00570) | [arXiv](https://arxiv.org/abs/2103.14024)

**摘要**: We introduce a method to render Neural Radiance Fields (NeRFs) in real time using PlenOctrees, an octree-based 3D representation which supports view-dependent effects. Our method can render 800×800 images at more than 150 FPS, which is over 3000 times faster than conventional NeRFs. We do so without sacrificing quality while preserving the ability of NeRFs to perform free-viewpoint rendering of scenes with arbitrary geometry and view-dependent effects. Real-time performance is achieved by pre-tabulating the NeRF into a PlenOctree. In order to preserve view-dependent effects such as specularities, we factorize the appearance via closed-form spherical basis functions. Specifically, we show that it is possible to train NeRFs to predict a spherical harmonic representation of radiance, removing the viewing direction as an input to the neural network. Furthermore, we show that PlenOctrees can be directly optimized to further minimize the reconstruction loss, which leads to equal or better quality compared to competing methods. Moreover, this octree optimization step can be used to reduce the training time, as we no longer need to wait for the NeRF training to converge fully. Our real-time neural rendering approach may potentially enable new applications such as 6-DOF industrial and product visualizations, as well as next generation AR/VR systems. PlenOctrees are amenable to in-browser rendering as well; please visit the project page for the interactive online demo, as well as video and code: https://alexyu.net/plenoctrees.

---

## 21. KiloNeRF: Speeding up Neural Radiance Fields with Thousands of Tiny MLPs

**作者**: Christian Reiser and Songyou Peng and Yiyi Liao and Andreas Geiger

**出处**: 2021 IEEE/CVF International Conference on Computer Vision (ICCV), 2021, 卷 null, 页 14315-14325

**链接**: [原文链接](https://www.semanticscholar.org/paper/c041aaed581616e122e790dd2769337216df3d8d) | [DOI](https://doi.org/10.1109/ICCV48922.2021.01407) | [arXiv](https://arxiv.org/abs/2103.13744)

**摘要**: NeRF synthesizes novel views of a scene with unprecedented quality by fitting a neural radiance field to RGB images. However, NeRF requires querying a deep Multi-Layer Perceptron (MLP) millions of times, leading to slow rendering times, even on modern GPUs. In this paper, we demonstrate that real-time rendering is possible by utilizing thousands of tiny MLPs instead of one single large MLP. In our setting, each individual MLP only needs to represent parts of the scene, thus smaller and faster-to-evaluate MLPs can be used. By combining this divide-and-conquer strategy with further optimizations, rendering is accelerated by three orders of magnitude compared to the original NeRF model without incurring high storage costs. Further, using teacher-student distillation for training, we show that this speed-up can be achieved without sacrificing visual quality.

---

## 22. Zip-NeRF: Anti-Aliased Grid-Based Neural Radiance Fields

**作者**: J. Barron and B. Mildenhall and Dor Verbin and Pratul P. Srinivasan and Peter Hedman

**出处**: 2023 IEEE/CVF International Conference on Computer Vision (ICCV), 2023, 卷 null, 页 19640-19648

**链接**: [原文链接](https://www.semanticscholar.org/paper/9eafa581e0268d471b9c61c87db79710dab9274e) | [DOI](https://doi.org/10.1109/ICCV51070.2023.01804) | [arXiv](https://arxiv.org/abs/2304.06706)

**摘要**: Neural Radiance Field training can be accelerated through the use of grid-based representations in NeRF’s learned mapping from spatial coordinates to colors and volumetric density. However, these grid-based approaches lack an explicit understanding of scale and therefore often introduce aliasing, usually in the form of jaggies or missing scene content. Anti-aliasing has previously been addressed by mip-NeRF 360, which reasons about sub-volumes along a cone rather than points along a ray, but this approach is not natively compatible with current grid-based techniques. We show how ideas from rendering and signal processing can be used to construct a technique that combines mip-NeRF 360 and grid-based models such as Instant NGP to yield error rates that are 8% – 77% lower than either prior technique, and that trains 24× faster than mip-NeRF 360.

---

## 23. Direct Voxel Grid Optimization: Super-fast Convergence for Radiance Fields Reconstruction

**作者**: Cheng Sun and Min Sun and Hwann-Tzong Chen

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2021, 卷 null, 页 5449-5459

**链接**: [原文链接](https://www.semanticscholar.org/paper/4f7eb65f8d3c1eeb97e30f7ac68977ff16e1e942) | [DOI](https://doi.org/10.1109/CVPR52688.2022.00538) | [arXiv](https://arxiv.org/abs/2111.11215)

**摘要**: We present a super-fast convergence approach to reconstructing the per-scene radiance field from a set of images that capture the scene with known poses. This task, which is often applied to novel view synthesis, is recently revolution-ized by Neural Radiance Field (NeRF) for its state-of-the-art quality and fiexibility. However, NeRF and its variants require a lengthy training time ranging from hours to days for a single scene. In contrast, our approach achieves NeRF-comparable quality and converges rapidly from scratch in less than 15 minutes with a single GPU. We adopt a representation consisting of a density voxel grid for scene geometry and a feature voxel grid with a shallow network for complex view-dependent appearance. Modeling with explicit and discretized volume representations is not new, but we propose two simple yet non-trivial techniques that contribute to fast convergence speed and high-quality output. First, we introduce the post-activation interpolation on voxel density, which is capable of producing sharp surfaces in lower grid resolution. Second, direct voxel density optimization is prone to suboptimal geometry solutions, so we robustify the optimization process by imposing several priors. Finally, evaluation on five inward-facing benchmarks shows that our method matches, if not surpasses, NeRF's quality, yet it only takes about 15 minutes to train from scratch for a new scene. Code: https://github.com/sunset1995/DirectVoxGO.

---

## 24. Block-NeRF: Scalable Large Scene Neural View Synthesis

**作者**: Matthew Tancik and Vincent Casser and Xinchen Yan and Sabeek Pradhan and B. Mildenhall and Pratul P. Srinivasan and J. Barron and Henrik Kretzschmar

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2022, 卷 null, 页 8238-8248

**链接**: [原文链接](https://www.semanticscholar.org/paper/d7d1bbade9453f0348fac8a5c60d131528b87fcf) | [DOI](https://doi.org/10.1109/CVPR52688.2022.00807) | [arXiv](https://arxiv.org/abs/2202.05263)

**摘要**: We present Block-NeRF, a variant of Neural Radiance Fields that can represent large-scale environments. Specifically, we demonstrate that when scaling NeRF to render city-scale scenes spanning multiple blocks, it is vital to de-compose the scene into individually trained NeRFs. This decomposition decouples rendering time from scene size, enables rendering to scale to arbitrarily large environments, and allows per-block updates of the environment. We adopt several architectural changes to make NeRF robust to data captured over months under different environmental conditions. We add appearance embeddings, learned pose refinement, and controllable exposure to each individual NeRF, and introduce a procedure for aligning appearance between adjacent NeRFs so that they can be seamlessly combined. We build a grid of Block-NeRFs from 2.8 million images to create the largest neural scene representation to date, capable of rendering an entire neighborhood of San Francisco.

---

## 25. NeXT: Towards High Quality Neural Radiance Fields via Multi-skip Transformer

**作者**: Yunxiao Wang and Yanjie Li and Peidong Liu and Tao Dai and Shutao Xia

**出处**: 2022

**链接**: [原文链接](https://www.semanticscholar.org/paper/06d113db9bf4490b25bf8dfb3c469ffa0debf41a) | [DOI](https://doi.org/10.1007/978-3-031-19824-3_5)

**摘要**: null

---

## 26. Plenoxels: Radiance Fields without Neural Networks

**作者**: Alex Yu and Sara Fridovich-Keil and Matthew Tancik and Qinhong Chen and B. Recht and Angjoo Kanazawa

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2021, 卷 null, 页 5491-5500

**链接**: [原文链接](https://www.semanticscholar.org/paper/e91f73aaef155391b5b07e6612f5346dea888f64) | [DOI](https://doi.org/10.1109/CVPR52688.2022.00542) | [arXiv](https://arxiv.org/abs/2112.05131)

**摘要**: We introduce Plenoxels (plenoptic voxels), a systemfor photorealistic view synthesis. Plenoxels represent a scene as a sparse 3D grid with spherical harmonics. This representation can be optimized from calibrated images via gradient methods and regularization without any neural components. On standard, benchmark tasks, Plenoxels are optimized two orders of magnitude faster than Neural Radiance Fields with no loss in visual quality. For video and code, please see https://alexyu.net/plenoxels.

---

## 27. Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields

**作者**: J. Barron and B. Mildenhall and Dor Verbin and Pratul P. Srinivasan and Peter Hedman

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2021, 卷 null, 页 5460-5469

**链接**: [原文链接](https://www.semanticscholar.org/paper/ec90ffa017a2cc6a51342509ce42b81b478aefb3) | [DOI](https://doi.org/10.1109/CVPR52688.2022.00539) | [arXiv](https://arxiv.org/abs/2111.12077)

**摘要**: Though neural radiance fields (NeRF) have demon-strated impressive view synthesis results on objects and small bounded regions of space, they struggle on “un-bounded” scenes, where the camera may point in any di-rection and content may exist at any distance. In this set-ting, existing NeRF-like models often produce blurry or low-resolution renderings (due to the unbalanced detail and scale of nearby and distant objects), are slow to train, and may exhibit artifacts due to the inherent ambiguity of the task of reconstructing a large scene from a small set of images. We present an extension of mip-NeRF (a NeRF variant that addresses sampling and aliasing) that uses a non-linear scene parameterization, online distillation, and a novel distortion-based regularizer to overcome the chal-lenges presented by unbounded scenes. Our model, which we dub “mip-NeRF 360” as we target scenes in which the camera rotates 360 degrees around a point, reduces mean-squared error by 57% compared to mip-NeRF, and is able to produce realistic synthesized views and detailed depth maps for highly intricate, unbounded real-world scenes.

---

## 28. Local Light Field Fusion: Practical View Synthesis with Prescriptive Sampling Guidelines

**作者**: B. Mildenhall

**出处**: 2019

**链接**: [原文链接](https://www.semanticscholar.org/paper/af39e137818ef8304ccea2ada546700de1dd2f8c)

**摘要**: null

---

## 29. pixelNeRF: Neural Radiance Fields from One or Few Images

**作者**: Alex Yu and Vickie Ye and Matthew Tancik and Angjoo Kanazawa

**出处**: 2021 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2020, 卷 null, 页 4576-4585

**链接**: [原文链接](https://www.semanticscholar.org/paper/4365f51fc270c55005adb794002685078a6fca1d) | [DOI](https://doi.org/10.1109/CVPR46437.2021.00455) | [arXiv](https://arxiv.org/abs/2012.02190)

**摘要**: We propose pixelNeRF, a learning framework that predicts a continuous neural scene representation conditioned on one or few input images. The existing approach for constructing neural radiance fields [27] involves optimizing the representation to every scene independently, requiring many calibrated views and significant compute time. We take a step towards resolving these shortcomings by introducing an architecture that conditions a NeRF on image inputs in a fully convolutional manner. This allows the network to be trained across multiple scenes to learn a scene prior, enabling it to perform novel view synthesis in a feed-forward manner from a sparse set of views (as few as one). Leveraging the volume rendering approach of NeRF, our model can be trained directly from images with no explicit 3D supervision. We conduct extensive experiments on ShapeNet benchmarks for single image novel view synthesis tasks with held-out objects as well as entire unseen categories. We further demonstrate the flexibility of pixelNeRF by demonstrating it on multi-object ShapeNet scenes and real scenes from the DTU dataset. In all cases, pixelNeRF outperforms current state-of-the-art baselines for novel view synthesis and single image 3D reconstruction. For the video and code, please visit the project website:https://alexyu.net/pixelnerf.

---

## 30. BARF: Bundle-Adjusting Neural Radiance Fields

**作者**: Chen-Hsuan Lin and Wei-Chiu Ma and A. Torralba and S. Lucey

**出处**: 2021 IEEE/CVF International Conference on Computer Vision (ICCV), 2021, 卷 null, 页 5721-5731

**链接**: [原文链接](https://www.semanticscholar.org/paper/33cc02f23c97a3daa835953b9d2784d0e1abf16e) | [DOI](https://doi.org/10.1109/ICCV48922.2021.00569) | [arXiv](https://arxiv.org/abs/2104.06405)

**摘要**: Neural Radiance Fields (NeRF) [31] have recently gained a surge of interest within the computer vision community for its power to synthesize photorealistic novel views of real-world scenes. One limitation of NeRF, however, is its requirement of accurate camera poses to learn the scene representations. In this paper, we propose Bundle-Adjusting Neural Radiance Fields (BARF) for training NeRF from imperfect (or even unknown) camera poses — the joint problem of learning neural 3D representations and registering camera frames. We establish a theoretical connection to classical image alignment and show that coarse-to-fine registration is also applicable to NeRF. Furthermore, we show that naïvely applying positional encoding in NeRF has a negative impact on registration with a synthesis-based objective. Experiments on synthetic and real-world data show that BARF can effectively optimize the neural scene representations and resolve large camera pose misalignment at the same time. This enables view synthesis and localization of video sequences from unknown camera poses, opening up new avenues for visual localization systems (e.g. SLAM) and potential applications for dense 3D mapping and reconstruction.

---

## 31. StylizedNeRF: Consistent 3D Scene Stylization as Stylized NeRF via 2D-3D Mutual Learning

**作者**: Yihua Huang and Yue He and Yu-Jie Yuan and Yu-Kun Lai and Lin Gao

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2022, 卷 null, 页 18321-18331

**链接**: [原文链接](https://www.semanticscholar.org/paper/6d987103091666709cacfb825278763e49df60cc) | [DOI](https://doi.org/10.1109/CVPR52688.2022.01780) | [arXiv](https://arxiv.org/abs/2205.12183)

**摘要**: 3D scene stylization aims at generating stylized images of the scene from arbitrary novel views following a given set of style examples, while ensuring consistency when rendered from different views. Directly applying methods for image or video stylization to 3D scenes cannot achieve such consistency. Thanks to recently proposed neural radiance fields (NeRF), we are able to represent a 3D scene in a consistent way. Consistent 3D scene stylization can be effectively achieved by stylizing the corresponding NeRF. However, there is a significant domain gap between style examples which are 2D images and NeRF which is an implicit volumetric representation. To address this problem, we propose a novel mutual learning framework for 3D scene stylization that combines a 2D image stylization network and NeRF to fuse the stylization ability of 2D stylization network with the 3D consistency of NeRF. We first pre-train a standard NeRF of the 3D scene to be stylized and replace its color prediction module with a style network to obtain a stylized NeRF. It is followed by distilling the prior knowledge of spatial consistency from NeRF to the 2D stylization network through an introduced consistency loss. We also introduce a mimic loss to supervise the mutual learning of the NeRF style module and fine-tune the 2D stylization decoder. In order to further make our model handle ambiguities of 2D stylization results, we introduce learnable latent codes that obey the probability distributions conditioned on the style. They are attached to training samples as conditional inputs to better learn the style module in our novel stylized NeRF. Experimental results demonstrate that our method is superior to existing approaches in both visual quality and long-range consistency.

---

## 32. NeRF in the Wild: Neural Radiance Fields for Unconstrained Photo Collections

**作者**: Ricardo Martin-Brualla and Noha Radwan and Mehdi S. M. Sajjadi and J. Barron and Alexey Dosovitskiy and Daniel Duckworth

**出处**: 2021 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2020, 卷 null, 页 7206-7215

**链接**: [原文链接](https://www.semanticscholar.org/paper/691eddbfaebbc71f6a12d3c99d5c155042459434) | [DOI](https://doi.org/10.1109/CVPR46437.2021.00713) | [arXiv](https://arxiv.org/abs/2008.02268)

**摘要**: We present a learning-based method for synthesizing novel views of complex scenes using only unstructured collections of in-the-wild photographs. We build on Neural Radiance Fields (NeRF), which uses the weights of a multi-layer perceptron to model the density and color of a scene as a function of 3D coordinates. While NeRF works well on images of static subjects captured under controlled settings, it is incapable of modeling many ubiquitous, real-world phenomena in uncontrolled images, such as variable illumination or transient occluders. We introduce a series of extensions to NeRF to address these issues, thereby enabling accurate reconstructions from unstructured image collections taken from the internet. We apply our system, dubbed NeRF-W, to internet photo collections of famous landmarks, and demonstrate temporally consistent novel view renderings that are significantly closer to photorealism than the prior state of the art.

---

## 33. Alma Mater Studiorum Università di Bologna Archivio istituzionale della ricerca

**出处**: null

**链接**: [原文链接](https://www.semanticscholar.org/paper/a18a15ce73d2999b99f6973a1af78959dc0f04cf)

**摘要**: null

---

## 34. IBRNet: Learning Multi-View Image-Based Rendering

**作者**: Qianqian Wang and Zhicheng Wang and Kyle Genova and Pratul P. Srinivasan and Howard Zhou and J. Barron and Ricardo Martin-Brualla and Noah Snavely and T. Funkhouser

**出处**: 2021 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2021, 卷 null, 页 4688-4697

**链接**: [原文链接](https://www.semanticscholar.org/paper/7cbc3dd0280b8c4551ac934af42dc227d43754f7) | [DOI](https://doi.org/10.1109/CVPR46437.2021.00466) | [arXiv](https://arxiv.org/abs/2102.13090)

**摘要**: We present a method that synthesizes novel views of complex scenes by interpolating a sparse set of nearby views. The core of our method is a network architecture that includes a multilayer perceptron and a ray transformer that estimates radiance and volume density at continuous 5D locations (3D spatial locations and 2D viewing directions), drawing appearance information on the fly from multiple source views. By drawing on source views at render time, our method hearkens back to classic work on image-based rendering (IBR), and allows us to render high-resolution imagery. Unlike neural scene representation work that optimizes per-scene functions for rendering, we learn a generic view interpolation function that generalizes to novel scenes. We render images using classic volume rendering, which is fully differentiable and allows us to train using only multi-view posed images as supervision. Experiments show that our method outperforms recent novel view synthesis methods that also seek to generalize to novel scenes. Further, if fine-tuned on each scene, our method is competitive with state-of-the-art single-scene neural rendering methods.1

---

## 35. NeRF

**作者**: B. Mildenhall and Pratul P. Srinivasan and Matthew Tancik and J. Barron and R. Ramamoorthi and Ren Ng

**出处**: Communications of the ACM, 2020, 卷 65, 页 99 - 106

**链接**: [原文链接](https://www.semanticscholar.org/paper/428b663772dba998f5dc6a24488fff1858a0899f) | [DOI](https://doi.org/10.1145/3503250) | [arXiv](https://arxiv.org/abs/2003.08934)

**摘要**: We present a method that achieves state-of-the-art results for synthesizing novel views of complex scenes by optimizing an underlying continuous volumetric scene function using a sparse set of input views. Our algorithm represents a scene using a fully connected (nonconvolutional) deep network, whose input is a single continuous 5D coordinate (spatial location (x, y, z) and viewing direction (θ, ϕ)) and whose output is the volume density and view-dependent emitted radiance at that spatial location. We synthesize views by querying 5D coordinates along camera rays and use classic volume rendering techniques to project the output colors and densities into an image. Because volume rendering is naturally differentiable, the only input required to optimize our representation is a set of images with known camera poses. We describe how to effectively optimize neural radiance fields to render photorealistic novel views of scenes with complicated geometry and appearance, and demonstrate results that outperform prior work on neural rendering and view synthesis.

---

## 36. TensoRF: Tensorial Radiance Fields

**作者**: Anpei Chen and Zexiang Xu and Andreas Geiger and Jingyi Yu and Hao Su

**出处**: ArXiv, 2022, 卷 abs/2203.09517, 页 null

**链接**: [原文链接](https://www.semanticscholar.org/paper/b4a9437302411abde0c9de784a14bfc6a5d950cf) | [DOI](https://doi.org/10.48550/arXiv.2203.09517) | [arXiv](https://arxiv.org/abs/2203.09517)

**摘要**: We present TensoRF, a novel approach to model and reconstruct radiance fields. Unlike NeRF that purely uses MLPs, we model the radiance field of a scene as a 4D tensor, which represents a 3D voxel grid with per-voxel multi-channel features. Our central idea is to factorize the 4D scene tensor into multiple compact low-rank tensor components. We demonstrate that applying traditional CP decomposition -- that factorizes tensors into rank-one components with compact vectors -- in our framework leads to improvements over vanilla NeRF. To further boost performance, we introduce a novel vector-matrix (VM) decomposition that relaxes the low-rank constraints for two modes of a tensor and factorizes tensors into compact vector and matrix factors. Beyond superior rendering quality, our models with CP and VM decompositions lead to a significantly lower memory footprint in comparison to previous and concurrent works that directly optimize per-voxel features. Experimentally, we demonstrate that TensoRF with CP decomposition achieves fast reconstruction (<30 min) with better rendering quality and even a smaller model size (<4 MB) compared to NeRF. Moreover, TensoRF with VM decomposition further boosts rendering quality and outperforms previous state-of-the-art methods, while reducing the reconstruction time (<10 min) and retaining a compact model size (<75 MB).

---

## 37. Point-NeRF: Point-based Neural Radiance Fields

**作者**: Qiangeng Xu and Zexiang Xu and J. Philip and Sai Bi and Zhixin Shu and Kalyan Sunkavalli and U. Neumann

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2022, 卷 null, 页 5428-5438

**链接**: [原文链接](https://www.semanticscholar.org/paper/055e87ce418a83d6fd555b73aea0d838385dfa85) | [DOI](https://doi.org/10.1109/CVPR52688.2022.00536) | [arXiv](https://arxiv.org/abs/2201.08845)

**摘要**: Volumetric neural rendering methods like NeRF [34] generate high-quality view synthesis results but are optimized per-scene leading to prohibitive reconstruction time. On the other hand, deep multi-view stereo methods can quickly reconstruct scene geometry via direct network inference. Point-NeRF combines the advantages of these two approaches by using neural 3D point clouds, with associated neural features, to model a radiance field. Point-NeRF can be rendered efficiently by aggregating neural point features near scene surfaces, in a ray marching-based rendering pipeline. Moreover, Point-NeRF can be initialized via direct inference of a pre-trained deep network to produce a neural point cloud; this point cloud can be finetuned to surpass the visual quality of NeRF with 30× faster training time. Point-NeRF can be combined with other 3D re-construction methods and handles the errors and outliers in such methods via a novel pruning and growing mechanism.

---

## 38. Instant neural graphics primitives with a multiresolution hash encoding

**作者**: T. Müller and Alex Evans and Christoph Schied and A. Keller

**出处**: ACM Transactions on Graphics (TOG), 2022, 卷 41, 页 1 - 15

**链接**: [原文链接](https://www.semanticscholar.org/paper/60e69982ef2920596c6f31d6fd3ca5e9591f3db6) | [DOI](https://doi.org/10.1145/3528223.3530127) | [arXiv](https://arxiv.org/abs/2201.05989)

**摘要**: Neural graphics primitives, parameterized by fully connected neural networks, can be costly to train and evaluate. We reduce this cost with a versatile new input encoding that permits the use of a smaller network without sacrificing quality, thus significantly reducing the number of floating point and memory access operations: a small neural network is augmented by a multiresolution hash table of trainable feature vectors whose values are optimized through stochastic gradient descent. The multiresolution structure allows the network to disambiguate hash collisions, making for a simple architecture that is trivial to parallelize on modern GPUs. We leverage this parallelism by implementing the whole system using fully-fused CUDA kernels with a focus on minimizing wasted bandwidth and compute operations. We achieve a combined speedup of several orders of magnitude, enabling training of high-quality neural graphics primitives in a matter of seconds, and rendering in tens of milliseconds at a resolution of 1920×1080.

---

## 39. HR-NeRF: advancing realism and accuracy in highlight scene representation

**作者**: Shufan Dai and Shanqin Wang

**出处**: Frontiers in Neurorobotics, 2025, 卷 19, 页 null

**链接**: [原文链接](https://www.semanticscholar.org/paper/8dbb5416a83b0ac7941dc838d2ccc7e0bd8c3d6d) | [DOI](https://doi.org/10.3389/fnbot.2025.1558948) | [PMID](https://pubmed.ncbi.nlm.nih.gov/40308477/)

**摘要**: NeRF and its variants excel in novel view synthesis but struggle with scenes featuring specular highlights. To address this limitation, we introduce the Highlight Recovery Network (HRNet), a new architecture that enhances NeRF's ability to capture specular scenes. HRNet incorporates Swish activation functions, affine transformations, multilayer perceptrons (MLPs), and residual blocks, which collectively enable smooth non-linear transformations, adaptive feature scaling, and hierarchical feature extraction. The residual connections help mitigate the vanishing gradient problem, ensuring stable training. Despite the simplicity of HRNet's components, it achieves impressive results in recovering specular highlights. Additionally, a density voxel grid enhances model efficiency. Evaluations on four inward-facing benchmarks demonstrate that our approach outperforms NeRF and its variants, achieving a 3–5 dB PSNR improvement on each dataset while accurately capturing scene details. Furthermore, our method effectively preserves image details without requiring positional encoding, rendering a single scene in ~18 min on an NVIDIA RTX 3090 Ti GPU.

---

## 40. Neural Scene Flow Fields for Space-Time View Synthesis of Dynamic Scenes

**作者**: Zhengqi Li and Simon Niklaus and Noah Snavely and Oliver Wang

**出处**: 2021 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2020, 卷 null, 页 6494-6504

**链接**: [原文链接](https://www.semanticscholar.org/paper/13034a395d5c6728c9b11e777828d9998018cbf6) | [DOI](https://doi.org/10.1109/CVPR46437.2021.00643) | [arXiv](https://arxiv.org/abs/2011.13084)

**摘要**: We present a method to perform novel view and time synthesis of dynamic scenes, requiring only a monocular video with known camera poses as input. To do this, we introduce Neural Scene Flow Fields, a new representation that models the dynamic scene as a time-variant continuous function of appearance, geometry, and 3D scene motion. Our representation is optimized through a neural network to fit the observed input views. We show that our representation can be used for varieties of in-the-wild scenes, including thin structures, view-dependent effects, and complex degrees of motion. We conduct a number of experiments that demonstrate our approach significantly outperforms recent monocular view synthesis methods, and show qualitative results of space-time view synthesis on a variety of real-world videos.

---

## 41. RegNeRF: Regularizing Neural Radiance Fields for View Synthesis from Sparse Inputs

**作者**: Michael Niemeyer and J. Barron and B. Mildenhall and Mehdi S. M. Sajjadi and Andreas Geiger and Noha Radwan

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2021, 卷 null, 页 5470-5480

**链接**: [原文链接](https://www.semanticscholar.org/paper/7163d171d4671ab8c0fd342e5280db532700999a) | [DOI](https://doi.org/10.1109/CVPR52688.2022.00540) | [arXiv](https://arxiv.org/abs/2112.00724)

**摘要**: Neural Radiance Fields (NeRF) have emerged as a powerful representation for the task of novel view synthesis due to their simplicity and state-of-the-art performance. Though NeRF can produce photorealistic renderings of unseen viewpoints when many input views are available, its performance drops significantly when this number is reduced. We observe that the majority of artifacts in sparse input scenarios are caused by errors in the estimated scene geometry, and by divergent behavior at the start of training. We address this by regularizing the geometry and appearance of patches rendered from unobserved viewpoints, and annealing the ray sampling space during training. We additionally use a normalizing flow model to regularize the color of unobserved viewpoints. Our model outperforms not only other methods that optimize over a single scene, but in many cases also conditional models that are extensively pre-trained on large multi-view datasets.

---

