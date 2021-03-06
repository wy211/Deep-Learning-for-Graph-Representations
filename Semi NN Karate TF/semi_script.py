import tensorflow as tf
import numpy as np
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA

def load_data():
	f = open('karate/input')
	f=f.readlines()
	features = np.eye(34)
	adj = np.zeros((34,34))
	for row in f:
		row_map = map(int,row.split(' '))
		for c in row_map[1:]:
			adj[row_map[0]-1][c-1]=1
			adj[c-1][row_map[0]-1]=1
        f=open('karate/labels')
        f=f.readlines()
        clas={}
        for row in f:
        	temp=row.strip().split('-')
        	for x in map(int,temp[0].split(',')):
	        	clas[x]=int(temp[1])
	y=tf.one_hot(np.array(clas.values()),4).eval(session=tf.Session())
	return adj,features,y,clas.values()

def glorot(shape):
	init_range = np.sqrt(6.0/(shape[0]+shape[1]))
	print (shape[0]+shape[1])
	initial = tf.random_uniform(shape,minval=-init_range,maxval=init_range,dtype=tf.float32)
	return tf.Variable(initial)

adj,features,y,q = load_data()
index = [0,2,4,8] # index of 1 labeled node per community
mask = np.array(np.zeros(y.shape[0]),dtype=bool)
mask[index]=True

new_y = np.zeros(y.shape)
new_y[index]=y[index]

adj = adj +  np.eye(adj.shape[0])
D = np.diag(np.power(adj.sum(1),-.5))
D[np.isinf(D)]=0.0
adj = np.dot(np.dot(D.T,adj),D)


support = tf.placeholder(tf.float32,shape=[None,None])
x = tf.placeholder(tf.float32,shape=[None,None])
labels = tf.placeholder(tf.float32,shape=[None,y.shape[1]])
act = tf.nn.tanh


sess=tf.Session()

w_1 = glorot([34,2])
h_1 = act(tf.matmul(tf.matmul(support,x),w_1))
#w_2 = glorot([2,2])
#h_2 = act(tf.matmul(tf.matmul(support,h_1),w_2))
#w_3 = glorot([2,2])
#h_3 = act(tf.matmul(tf.matmul(support,h_2),w_3))
w_3 = glorot([2,4])
h_3 = act(tf.matmul(tf.matmul(support,h_1),w_3))
#w_5 = glorot([2,4])
#h_5 = act(tf.matmul(tf.matmul(support,h_4),w_5))

predict = tf.nn.softmax(h_3)

feed_dict = { support: adj, x:features,labels:new_y}

def loss(pred,y,mask):
	loss = tf.nn.softmax_cross_entropy_with_logits(pred,y)
	mask = tf.cast(mask,dtype=tf.float32)
	mask = mask / tf.reduce_mean(mask)
	loss = loss * mask
	return tf.reduce_mean(loss)

def accuracy(pred,y,mask):
	acc=tf.equal(tf.argmax(pred,1),tf.argmax(y,1))
	acc = tf.cast(acc,tf.float32)
	mask = tf.cast(mask,dtype=tf.float32)
	mask = mask /tf.reduce_mean(mask)
	acc = acc * mask
	return tf.reduce_mean(acc)

loss_=0

for weight in [w_1,w_3]:
	loss_ = loss_ + .001 * tf.nn.l2_loss(weight)

loss_ = loss_ + loss(predict,labels,mask)
acc_ = accuracy(predict,labels,mask)
opt = tf.train.AdamOptimizer(learning_rate=0.01).minimize(loss_)
sess.run(tf.initialize_all_variables())

for i in xrange(300):
	out = sess.run([opt,loss_],feed_dict=feed_dict)
	acc = sess.run(acc_,feed_dict=feed_dict)
	print out,acc

viz = sess.run([h_1,h_3],feed_dict=feed_dict)
#pca = PCA(n_components=2)
#viz=pca.fit_transform(viz)
color=['r','g','b','m']
q=np.array(q)
for i in viz:
	for val in xrange(4):
		plt.scatter(i[:,0][q==val],i[:,1][q==val],c=color[val],s=100,label='Class '+str(val))
	plt.legend()
	plt.show()
	print i.shape
	break
