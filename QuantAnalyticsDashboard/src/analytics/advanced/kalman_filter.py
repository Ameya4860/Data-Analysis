import numpy as np

class KalmanFilterHedge:
    def __init__(self, delta=1e-4, R=1e-3, Q=1e-3):
        self.delta = delta # system noise variance
        self.R = R         # measurement noise variance
        
        # State: [beta, alpha] (slope, intercept)
        self.x = np.zeros(2) 
        self.P = np.zeros((2, 2)) # covariance matrix
        self.initialized = False

    def update(self, price_y, price_x):
        # Observation matrix H = [price_x, 1]
        H = np.array([price_x, 1.0])
        
        if not self.initialized:
            self.x = np.array([0.0, 0.0]) # Initial guess
            self.P = np.eye(2)
            self.initialized = True
            return 0.0

        # Prediction step
        # x_k|k-1 = x_k-1|k-1 (Random walk assumption)
        # P_k|k-1 = P_k-1|k-1 + Q
        # Here we treat Q as process noise covariance
        # Q matrix for 2 states
        Q_mat = np.eye(2) * self.delta
        
        x_pred = self.x
        P_pred = self.P + Q_mat
        
        # Update step
        # y = z - H * x_pred
        y_residual = price_y - np.dot(H, x_pred)
        
        # S = H * P_pred * H.T + R
        S = np.dot(H, np.dot(P_pred, H.T)) + self.R
        
        # K = P_pred * H.T * S^-1
        K = np.dot(P_pred, H.T) / S
        
        # x_new = x_pred + K * y
        self.x = x_pred + K * y_residual
        
        # P_new = (I - K * H) * P_pred
        self.P = np.dot((np.eye(2) - np.outer(K, H)), P_pred)
        
        return self.x[0] # Return beta
