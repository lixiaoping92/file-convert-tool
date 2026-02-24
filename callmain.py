import consv_status
convsp_path = str("D:/WeldRobotWeldRobot1.0/ptom/publish/CONVSP.EXE")
status = consv_status.call_convsp(convsp_path, args=["234.txt","111111.s"])
if status['success']:
    print("successful！！！转换成功！！！")
else:
    print('转换失败: ' + status['stderr'])


