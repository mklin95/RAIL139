# RAIL (Rail AI Image Location)

An image-to-text retrieval framework for railway image geolocation under limited-computing-resource conditions. 

RAIL employs a domain-specific multimodal semantic tagging framework to convert railway images into hierarchical textual features, which are then retrieved using TF-IDF weighting and cosine similarity. 

Experiments on the Taiwan Rail way Chaozhou–Fangshan corridor, using 139 training images from 19 locations and 24 heterogeneous test images, show that RAIL achieved Top-1 to Top-4 accuracies of 0.708, 0.833, 0.917, and 0.958, respectively. Compared with CLIP@RTX-1060, RAIL delivered substantially higher retrieval accuracy and lower latency. Although CLIP@A100 with ViT-H-14 achieved slightly better Top-1 and Top-2 performance, RAIL matched it at Top-4 accuracy (0.958) while requiring far less computational cost and avoiding continuous GPU occupation during retrieval. These results show that RAIL provides an interpretable, efficient, and deployment-friendly solution for railway image geolocation.